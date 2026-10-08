from researchops.cache import SQLiteCache
from researchops.models import FetchParams
from researchops.tools.fetch import SecureFetchTool


cache = SQLiteCache(
    "data/fetch_cache.sqlite3"
)

fetch_tool = SecureFetchTool(
    cache
)


params = FetchParams(
    url="https://example.com",
    max_chars=5000
)


result = fetch_tool.fetch(
    params
)


print("\nTitle:")
print(result.title)

print("\nURL:")
print(result.url)

print("\nContent Type:")
print(result.content_type)

print("\nText:")
print(result.text[:1000])