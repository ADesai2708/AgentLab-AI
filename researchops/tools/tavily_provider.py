from tavily import TavilyClient

from researchops.config import TAVILY_API_KEY


class TavilySearchProvider:

    def __init__(self):

        if not TAVILY_API_KEY:
            raise RuntimeError(
                "TAVILY_API_KEY is not configured."
            )

        self.client = TavilyClient(
            api_key=TAVILY_API_KEY
        )

    def search(
        self,
        query: str,
        max_results: int
    ) -> list[dict]:

        response = self.client.search(
            query=query,
            max_results=max_results
        )

        results = []

        for item in response.get(
            "results",
            []
        ):

            results.append(
                {
                    "title": item.get(
                        "title",
                        ""
                    ),

                    "url": item.get(
                        "url"
                    ),

                    "snippet": item.get(
                        "content",
                        ""
                    ),

                    "score": item.get(
                        "score"
                    ),

                    "source": "tavily"
                }
            )

        return results