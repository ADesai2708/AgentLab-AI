from researchops.cache import SQLiteCache
from researchops.models import SearchParams
from researchops.tools.search import SearchTool


def mock_search_provider(
    query: str,
    max_results: int
):

    print("MOCK SEARCH PROVIDER CALLED")

    return [
        {
            "title": "Retrieval-Augmented Generation",
            "url": "https://example.com/rag",
            "snippet": "RAG combines retrieval with language generation.",
            "score": 0.95,
            "source": "mock"
        }
    ]


cache = SQLiteCache(
    "data/search_cache.sqlite3"
)


search_tool = SearchTool(
    cache=cache,
    provider=mock_search_provider
)


params = SearchParams(
    query="What is RAG?",
    max_results=5
)


print("\nFirst search:\n")

results = search_tool.search(params)

for result in results:
    print(result)


print("\nSecond search:\n")

results = search_tool.search(params)

for result in results:
    print(result)