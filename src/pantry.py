"""
pantry.py — "cook with what I have." YOUR CENTERPIECE.

⚠️  THIS IS YOUR SECOND DIFFERENTIATOR AND THE STAR FEATURE.
    Build it in two passes so you have a baseline -> improved STORY to tell.
    Understand the ranking logic cold; do not outsource the thinking here.

PASS 1 (baseline): rank recipes by number of missing ingredients (fewest = best),
using fuzzy name matching so "chicken" matches "chicken breast".

PASS 2 (improved): not all missing ingredients are equal.
    - Weight by how CORE a missing item is (missing the protein hurts more
      than a missing spice/garnish).
    - Consider SUBSTITUTABILITY (missing butter is more forgivable than
      missing the main vegetable).
    - Optionally fold in a "pantry staples" set (salt, water, oil) that you
      assume everyone has, so they never count as missing.

Document your weighting choices in the README — that reasoning IS the skill.
"""

from . import storage
from .normalize import names_match

# Assume everyone has these; don't penalize recipes for needing them.
STAPLES = {"salt", "water", "pepper", "oil"}


def _recipe_ingredient_names(recipe: dict) -> list[str]:
    """Prefer the pre-extracted ner names; fall back to raw strings."""
    # `ner` (RecipeNLG's named-entity-recognized ingredient names) is already
    # clean ("chicken breast" not "2 lbs. chicken breast, diced"), so prefer
    # it over the raw `ingredients` strings whenever it's present.
    return recipe.get("ner") or recipe.get("ingredients", [])


def _missing_ingredients(have: list[str], recipe: dict) -> list[str]:
    """Which recipe ingredients are NOT covered by the pantry list."""
    missing = []
    for ing in _recipe_ingredient_names(recipe):
        name = ing.lower().strip()
        if name in STAPLES:
            # Assumed always on hand (salt, water, etc.) — never counts as missing.
            continue
        # `have` is the user's pantry list; `names_match` does fuzzy word-level
        # comparison (e.g. "chicken" in `have` satisfies "chicken breast" here),
        # so an ingredient is only "missing" if NONE of the pantry items match it.
        if not any(names_match(h, name) for h in have):
            missing.append(name)
    return missing


def match_pantry_baseline(have: list[str], k: int = 10) -> list[dict]:
    """PASS 1: rank by fewest missing ingredients. Build this first."""
    results = []
    for r in storage.get_all_recipes():
        missing = _missing_ingredients(have, r)
        results.append({
            "id": r["id"],
            "title": r["title"],
            "missing": missing,
            "missing_count": len(missing),
        })
    # Fewest missing ingredients first — the naive "most cookable" ordering
    # PASS 1 is meant to establish as a baseline to improve on in PASS 2.
    results.sort(key=lambda x: x["missing_count"])
    return results[:k]


def _ingredient_weight(name: str) -> float:
    """
    PASS 2 helper: how much does missing THIS ingredient hurt?
    TODO(you): design this. A simple, defensible start:
      - staples: 0 (already filtered)
      - "core" proteins/vegetables: high weight
      - spices/herbs/garnishes: low weight
    You could hard-code a small keyword map, or derive weight from how often
    an ingredient appears across all recipes (rare -> probably core to THIS dish).
    Whatever you choose, EXPLAIN IT in the README.
    """
    return 1.0  # placeholder — replace with real weighting; currently == PASS 1 behavior


def match_pantry(have: list[str], k: int = 10, where: dict | None = None) -> list[dict]:
    """
    PASS 2: weighted pantry match. Lower score = more cookable.
    `where` reserved for later metadata filtering (time/dietary).
    """
    results = []
    for r in storage.get_all_recipes():
        missing = _missing_ingredients(have, r)
        # Sum of per-ingredient weights, not just a count — this is what lets
        # "missing the protein" outweigh "missing a garnish" once
        # `_ingredient_weight` is implemented for real.
        score = sum(_ingredient_weight(m) for m in missing)
        results.append({
            "id": r["id"],
            "title": r["title"],
            "missing": missing,
            "score": round(score, 2),
        })
    # Lower weighted score first (best match/most cookable).
    results.sort(key=lambda x: x["score"])
    return results[:k]


if __name__ == "__main__":
    have = ["flour", "eggs", "milk", "sugar", "butter"]
    print("BASELINE:")
    for r in match_pantry_baseline(have, k=5):
        print(f"  {r['title']} — missing {r['missing_count']}: {r['missing']}")
