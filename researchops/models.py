from pydantic import BaseModel, Field, HttpUrl


class SearchParams(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=1000
    )

    max_results: int = Field(
        default=5,
        ge=1,
        le=10
    )


class SearchResult(BaseModel):
    title: str

    url: HttpUrl

    snippet: str = ""

    score: float | None = None

    source: str = "search"
class FetchParams(BaseModel):
    url: HttpUrl

    max_chars: int = Field(
        default=20000,
        ge=1000,
        le=100000
    )
class FetchResult(BaseModel):
    url: HttpUrl

    title: str = ""

    text: str

    content_type: str = "text/html"

    truncated: bool = False

    source: str = "fetch"

class CalculatorParams(BaseModel):
    expression: str = Field(
        min_length=1,
        max_length=500
    )


class CalculatorResult(BaseModel):
    expression: str
    result: float
    source: str = "calculator"
class DocumentChunk(BaseModel):
    document_id: str
    chunk_id: str
    text: str
    page_number: int | None = None
    source: str