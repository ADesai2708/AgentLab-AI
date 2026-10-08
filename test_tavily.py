from researchops.cache import SQLiteCache
from researchops.models import SearchParams
from researchops.tools.search import SearchTool
from researchops.tools.tavily_provider import TavilySearchProvider


provider = TavilySearchProvider()


cache = SQLiteCache(
    "data/tavily_cache.sqlite3"
)


search_tool = SearchTool(
    cache=cache,
    provider=provider.search
)


params = SearchParams(
    query="What is retrieval augmented generation?",
    max_results=5
)


results = search_tool.search(params)


for i, result in enumerate(
    results,
    start=1
):

    print(f"\nResult {i}")

    print("Title:", result.title)

    print("URL:", result.url)

    print("Score:", result.score)

    print("Snippet:", result.snippet[:300])