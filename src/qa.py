import os
from dotenv import load_dotenv
from anthropic import Anthropic
from . import embeddings, storage

load_dotenv()
_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def _build_context(recipe_ids: list[int]) -> str:
    blocks = []
    for rid in recipe_ids:
        r = storage.get_recipe(rid)
        if not r:
            continue
        ings = "; ".join(r.get("ingredients", []))
        steps = " ".join(r.get("steps", []))
        blocks.append(f"[Recipe {rid}] {r['title']}\nIngredients: {ings}\nSteps: {steps}")
    return "\n\n".join(blocks)


def ask(question: str, k: int = 4, where: dict | None = None) -> dict:
    """
    Answer `question` using the most relevant stored recipes.
    Returns {"answer": str, "sources": [{"id", "title"}]}.
    """
    hits = embeddings.semantic_search(question, k=k, where=where)
    context = _build_context([h["id"] for h in hits])

    prompt = f"""You are a cooking assistant. Answer the user's question using ONLY the recipes provided below as context. If the recipes don't contain the answer, say so honestly rather than inventing one. When you use a recipe, cite it by its title.

Context recipes:
{context}

User question: {question}"""

    msg = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = "".join(b.text for b in msg.content if b.type == "text")

    return {
        "answer": answer,
        "sources": [{"id": h["id"], "title": h["title"]} for h in hits],
    }


if __name__ == "__main__":
    out = ask("What can I make with chickpeas and spinach?")
    print(out["answer"])
    print("\nSources:", [s["title"] for s in out["sources"]])
