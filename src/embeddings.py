"""
embeddings.py — embed recipes and enable semantic + metadata-filtered search.

This layer is mostly standard and safe to lean on AI for — BUT understand
these two ideas because they're the interview talking points:
  - You embed a TEXT REPRESENTATION of each recipe (title + ingredients +
    cuisine). What you put in the text changes what "similar" means.
  - Metadata (cuisine, total_time, dietary_tags) is stored alongside vectors
    so you can FILTER before semantic search — e.g. "dairy-free under 30 min"
    narrows the set, then similarity ranks within it. This combo is what makes
    both the pantry feature and the Q&A feature good.

Build order: AFTER storage.py works and you've seeded some recipes.
"""

import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer
from . import storage

CHROMA_DIR = str(Path(__file__).parent.parent / "chroma")
COLLECTION = "recipes"

# Small, fast, free, good enough. all-MiniLM-L6-v2 is the standard starter.
_model = SentenceTransformer("all-MiniLM-L6-v2")
_client = chromadb.PersistentClient(path=CHROMA_DIR)


def _recipe_to_text(recipe: dict) -> str:
    """The text that gets embedded. Tweak this and observe how results change."""
    ingredients = ", ".join(recipe.get("ner") or recipe.get("ingredients", []))
    return f"{recipe['title']}. Ingredients: {ingredients}. Cuisine: {recipe.get('cuisine') or 'unknown'}."


def index_all_recipes():
    """Embed every recipe in the DB and store in Chroma with metadata."""
    col = _client.get_or_create_collection(COLLECTION)
    recipes = storage.get_all_recipes()

    ids, docs, metas = [], [], []
    for r in recipes:
        ids.append(str(r["id"]))
        docs.append(_recipe_to_text(r))
        metas.append({
            "title": r["title"],
            "cuisine": r.get("cuisine") or "",
            "total_time": r.get("total_time") or -1,
            "dietary_tags": ",".join(r.get("dietary_tags", [])),
        })

    embeddings = _model.encode(docs, show_progress_bar=True).tolist()
    # Chroma has batch-size limits; chunk if the subset is large.
    B = 5000
    for i in range(0, len(ids), B):
        col.upsert(
            ids=ids[i:i+B],
            documents=docs[i:i+B],
            embeddings=embeddings[i:i+B],
            metadatas=metas[i:i+B],
        )
    print(f"indexed {len(ids)} recipes")


def semantic_search(query: str, k: int = 5, where: dict | None = None) -> list[dict]:
    """
    Return the k most semantically similar recipes to `query`.
    `where` is an optional Chroma metadata filter, e.g.
        {"total_time": {"$lte": 30}}  or  {"cuisine": "Italian"}
    Returns list of {id, title, distance} — fetch full records via storage.get_recipe.
    """
    col = _client.get_or_create_collection(COLLECTION)
    q_emb = _model.encode([query]).tolist()
    res = col.query(query_embeddings=q_emb, n_results=k, where=where)
    out = []
    for i, rid in enumerate(res["ids"][0]):
        out.append({
            "id": int(rid),
            "title": res["metadatas"][0][i]["title"],
            "distance": res["distances"][0][i],
        })
    return out
