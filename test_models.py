from researchops.models import SearchParams


request = SearchParams(
    query="What is retrieval augmented generation?",
    max_results=5
)

print(request)