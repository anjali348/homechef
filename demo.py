"""
demo.py — run the whole Phase 1 pipeline from one place.

This is your proof that the ML core works BEFORE any web layer exists.
When this runs cleanly, Phase 1 is done and Phase 2 (FastAPI) is just
wrapping these same function calls in endpoints.

Usage:
    python -m src.seed          # 1. populate the DB (run once)
    python -m src.embeddings    # 2. build the vector index (run once)
    python demo.py              # 3. exercise everything
"""

from src import pantry, qa, embeddings


def main():
    print("=" * 60)
    print("SEMANTIC SEARCH")
    print("=" * 60)
    for hit in embeddings.semantic_search("warm comforting winter soup", k=3):
        print(f"  {hit['title']}  (distance {hit['distance']:.3f})")

    print("\n" + "=" * 60)
    print("PANTRY MATCH (baseline)")
    print("=" * 60)
    have = ["chicken", "rice", "onion", "garlic", "tomato"]
    for r in pantry.match_pantry_baseline(have, k=5):
        print(f"  {r['title']} — missing {r['missing_count']}: {r['missing']}")

    print("\n" + "=" * 60)
    print("RAG Q&A")
    print("=" * 60)
    out = qa.ask("What can I make with chickpeas and spinach?")
    print(out["answer"])
    print("\nSources:", [s["title"] for s in out["sources"]])


if __name__ == "__main__":
    main()
