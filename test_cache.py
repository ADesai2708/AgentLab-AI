from researchops.cache import SQLiteCache


cache = SQLiteCache(
    "data/test_cache.sqlite3"
)


key = cache.create_key(
    "test",
    {
        "question": "What is RAG?"
    }
)


print("Generated key:")
print(key)


print("\nBefore storing:")
print(cache.get(key))


cache.set(
    key,
    {
        "answer": "RAG stands for Retrieval Augmented Generation."
    }
)


print("\nAfter storing:")
print(cache.get(key))