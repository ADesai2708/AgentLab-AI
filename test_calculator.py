import pytest

from researchops.models import CalculatorParams
from researchops.tools.calculator import CalculatorTool


calculator = CalculatorTool()


def test_basic_calculation():
    result = calculator.calculate(
        CalculatorParams(expression="10 + 5")
    )

    assert result.result == 15.0


def test_complex_calculation():
    result = calculator.calculate(
        CalculatorParams(
            expression="(150 - 120) / 120 * 100"
        )
    )

    assert result.result == 25.0


def test_power():
    result = calculator.calculate(
        CalculatorParams(expression="2 ** 10")
    )

    assert result.result == 1024.0


def test_division():
    result = calculator.calculate(
        CalculatorParams(expression="10 / 4")
    )

    assert result.result == 2.5


def test_invalid_expression():
    with pytest.raises(ValueError):
        calculator.calculate(
            CalculatorParams(
                expression="invalid expression"
            )
        )


def test_dangerous_expression():
    with pytest.raises(ValueError):
        calculator.calculate(
            CalculatorParams(
                expression="__import__('os').system('whoami')"
            )
        )


def test_division_by_zero():
    with pytest.raises(ValueError):
        calculator.calculate(
            CalculatorParams(expression="10 / 0")
        )