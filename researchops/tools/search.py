from typing import Callable

from researchops.cache import SQLiteCache
from researchops.models import SearchParams, SearchResult


class SearchTool:

    def __init__(
        self,
        cache: SQLiteCache,
        provider: Callable[
            [str, int],
            list[dict]
        ]
    ):
        self.cache = cache
        self.provider = provider

    def search(
        self,
        params: SearchParams
    ) -> list[SearchResult]:

        # 1. Create deterministic cache key
        cache_key = self.cache.create_key(
            "search",
            params.model_dump()
        )

        # 2. Check cache
        cached = self.cache.get(cache_key)

        if cached is not None:

            print("CACHE HIT")

            return [
                SearchResult.model_validate(item)
                for item in cached
            ]

        print("CACHE MISS")

        # 3. Call search provider
        raw_results = self.provider(
            params.query,
            params.max_results
        )

        # 4. Validate provider response
        results = [
            SearchResult.model_validate(item)
            for item in raw_results
        ]

        # 5. Store in cache
        self.cache.set(
            cache_key,
            [
                result.model_dump(mode="json")
                for result in results
            ]
        )

        return results