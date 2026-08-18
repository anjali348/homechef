"""
normalize.py — turn messy ingredient text into structured, matchable data.

The problem: raw ingredient strings from RecipeNLG look like
    "1 c. firmly packed brown sugar"
    "1/2 tsp. vanilla"
    "3 1/2 c. bite size shredded rice biscuits"
    "2-3 cloves garlic, minced"
You need to extract {qty, unit, name} and normalize the name so that
"chicken breast" and "chicken" can match during pantry lookup.

Suggested approach (build incrementally, test on ugly inputs):
  1. Parse leading quantity (handle fractions like "1/2", mixed "3 1/2",
     ranges like "2-3").
  2. Parse the unit against a known unit vocabulary (c./cup/cups -> "cup",
     tsp./teaspoon -> "tsp", etc.).
  3. Whatever remains is the name — strip prep words ("minced", "sifted",
     "firmly packed") and lowercase.
  4. For matching, use rapidfuzz for fuzzy comparison so minor variants align.

SHORTCUT for the MVP: RecipeNLG already gives you a `ner` field with the
core name pre-extracted. Use `ner` for pantry MATCHING to get a working
system fast, and use THIS module to parse the raw strings for qty/unit and
to show the real normalization skill. Both, not either.
"""

from fractions import Fraction
from rapidfuzz import fuzz

# Extend these as you meet more variants in the real data.
UNIT_ALIASES = {
    "c": "cup", "c.": "cup", "cup": "cup", "cups": "cup",
    "tsp": "tsp", "tsp.": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    "tbsp": "tbsp", "tbsp.": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
    "oz": "oz", "oz.": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lb.": "lb", "pound": "lb", "pounds": "lb",
    "g": "g", "gram": "g", "grams": "g",
    "pkg": "package", "pkg.": "package",
    "qt": "quart", "qt.": "quart",
    "carton": "carton",
    "box": "box",
    "pint": "pint", "pint": "pt.", "pint" : "pt",
    "container": "container"
}

PREP_WORDS = {
    "minced", "chopped", "diced", "sifted", "melted", "softened",
    "packed", "firmly", "beaten", "crushed", "shredded", "grated",
    "fresh", "freshly", "large", "small", "medium",
}


def _parse_quantity(tokens: list[str]) -> tuple[float | None, list[str]]:
    """
    Read a leading quantity from tokens. Handles "1", "1/2", "3 1/2", "2-3".
    Returns (quantity_or_None, remaining_tokens).
    TODO(you): flesh out the range + mixed-number handling and test it.
    """
    if not tokens:
        return None, tokens

    first = tokens[0]

    # Range like "2-3": just take the low end, drop the rest of the token.
    if "-" in first and all(p.replace("/", "").isdigit() for p in first.split("-")):
        first = first.split("-")[0]

    # First token must at least be a number (whole or a fraction like "1/2").
    try:
        qty = float(Fraction(first))
    except (ValueError, ZeroDivisionError):
        return None, tokens

    remaining = tokens[1:]

    # Mixed number like "3 1/2": second token is also a number, and
    # specifically a fraction (has a "/"), so add it in and consume it.
    if remaining:
        second = remaining[0]
        is_number = True
        try:
            Fraction(second)
        except (ValueError, ZeroDivisionError):
            is_number = False

        if is_number and "/" in second:
            qty += float(Fraction(second))
            remaining = remaining[1:]  # move past the fraction token

    # Whatever is left in `remaining` now starts at the unit (e.g. "cup"),
    # ready for the caller's UNIT_ALIASES check.
    return qty, remaining


def normalize_ingredient(raw: str) -> dict:
    """
    Parse one raw ingredient string into {qty, unit, name}.
    Returns e.g. {"qty": 0.5, "unit": "cup", "name": "brown sugar", "raw": "..."}.
    TODO(you): this is a starting point — improve parsing and test on the
    ugliest examples you can find in RecipeNLG.
    """
    raw_clean = raw.lower().replace(",", " ").strip()
    tokens = raw_clean.split()

    qty, tokens = _parse_quantity(tokens)

    # Skip a parenthesized aside like "(6 oz.)" in "1 (6 oz.) pkg." — it's
    # a more precise measurement, not the unit token we're looking for.
    if tokens and tokens[0].startswith("("):
        while tokens and ")" not in tokens[0]:
            tokens = tokens[1:]
        if tokens:
            tokens = tokens[1:]  # drop the closing token itself, e.g. "oz.)"

    unit = None
    if tokens and tokens[0] in UNIT_ALIASES:
        unit = UNIT_ALIASES[tokens[0]]
        tokens = tokens[1:]

    name_tokens = [t for t in tokens if t not in PREP_WORDS]
    name = " ".join(name_tokens).strip()

    return {"qty": qty, "unit": unit, "name": name, "raw": raw}


DIFFERENT_PRODUCT = {"broth", "stock", "sauce", "powder", "extract", "oil", "juice"}

def names_match(a: str, b: str, threshold: int = 85) -> bool:
    """
    Does pantry item `a` satisfy recipe ingredient `b`?
    Layered: stop-list guard -> word-level fuzzy match.
    """
    a = a.lower().strip()
    b_words = b.lower().split()

    for word in b_words:
        if word in DIFFERENT_PRODUCT and a not in DIFFERENT_PRODUCT:
            return False

    for word in b_words:
        if fuzz.ratio(a, word) >= threshold:
            return True

    return False
if __name__ == "__main__":
    from . import storage
    recipes = storage.get_all_recipes()
    for r in recipes[:20]:
        for ing in r["ingredients"]:
            print(f"{ing!r:50} -> {normalize_ingredient(ing)}")