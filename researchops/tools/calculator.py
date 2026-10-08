import ast
import operator as op

from researchops.models import CalculatorParams, CalculatorResult


_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def _evaluate(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numeric constants are allowed.")

    if isinstance(node, ast.UnaryOp):
        operator = _ALLOWED_OPERATORS.get(type(node.op))

        if operator is None:
            raise ValueError("Unsupported unary operator.")

        return operator(_evaluate(node.operand))

    if isinstance(node, ast.BinOp):
        operator = _ALLOWED_OPERATORS.get(type(node.op))

        if operator is None:
            raise ValueError("Unsupported operator.")

        return operator(
            _evaluate(node.left),
            _evaluate(node.right)
        )

    raise ValueError("Invalid mathematical expression.")


class CalculatorTool:

    def calculate(
        self,
        params: CalculatorParams
    ) -> CalculatorResult:

        try:
            tree = ast.parse(
                params.expression,
                mode="eval"
            )

            result = _evaluate(tree.body)

        except (SyntaxError, ValueError, ZeroDivisionError) as exc:
            raise ValueError(
                f"Invalid calculation: {exc}"
            ) from exc

        if not isinstance(result, (int, float)):
            raise ValueError("Calculation did not produce a number.")

        return CalculatorResult(
            expression=params.expression,
            result=float(result)
        )