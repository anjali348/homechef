from src.embeddings import semantic_search
for hit in semantic_search("indian vegetarian curry", k=5):
    print(hit["title"], round(hit["distance"], 3))