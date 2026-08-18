"""
seed.py — load a manageable RecipeNLG subset into storage, then index it.

RecipeNLG is ~2M recipes. DO NOT load all of it. Take a few thousand for the
MVP — plenty for a good demo, and keeps embedding time/memory sane.

Source: the raw Kaggle CSV (data/raw/RecipeNLG_dataset.csv), not the
Hugging Face Hub loader — the Hub copy requires trust_remote_code and,
even then, gates behind a manual download from recipenlg.cs.put.poznan.pl.
Easier to just read the CSV we already have on disk directly.

RecipeNLG_dataset.csv columns: an unnamed row-index column, title,
ingredients (list of raw strings), directions (list of steps), link,
source, NER (list of core ingredient names). The list-valued columns are
stored as Python-literal strings (e.g. '["a", "b"]'), not JSON — hence
ast.literal_eval below rather than json.loads.
Note: it does NOT ship cuisine / total_time / dietary_tags — those are yours
to leave null for now, or derive later as an enhancement.

Run once to populate the DB, then embeddings.index_all_recipes() to vectorize.
"""

import ast
import csv
from pathlib import Path

from . import storage

CSV_PATH = Path(__file__).parent.parent / "data" / "raw" / "RecipeNLG_dataset.csv"

MIN_INGREDIENTS = 3  # fewer than this is usually junk / too trivial to pantry-match

# The CSV is ~2.3GB with some very large text fields (long directions/ingredient
# lists); csv's default per-field size cap is too small for a few of these rows.
csv.field_size_limit(10_000_000)


def _parse_list(raw: str) -> list:
    """
    Parse one of the CSV's stringified-list columns, e.g. '["a", "b"]'.
    Returns [] for empty/malformed cells instead of raising, since a few
    rows in a 2M-row scrape are expected to be corrupt.
    """
    if not raw:
        return []
    try:
        value = ast.literal_eval(raw)
        return value if isinstance(value, list) else []
    except (ValueError, SyntaxError):
        return []


def is_usable(row: dict) -> bool:
    """
    Decide whether a recipe is complete enough to include.
    Each check maps to a feature that would otherwise break:
      - title        -> needed to display and cite a recipe
      - directions   -> the RAG Q&A has nothing to answer from without steps
      - ner          -> the pantry matcher compares the user's pantry against
                        these core names; empty ner = can't participate at all
      - ingredients  -> too few ingredients isn't a real, useful recipe
    """
    if not row.get("title"):
        return False
    if not row.get("directions"):
        return False
    if not row.get("ner"):
        return False
    if len(row.get("ingredients") or []) < MIN_INGREDIENTS:
        return False
    return True


def seed(n: int = 5000):
    storage.init_db()

    count = 0       # usable recipes actually stored
    scanned = 0     # total rows looked at (to report how much we skipped)

    # newline="" is required by the csv module to handle quoted fields that
    # contain embedded newlines (directions text often does) correctly.
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for raw_row in reader:
            if count >= n:
                break
            scanned += 1

            row = {
                "title": raw_row["title"],
                "ingredients": _parse_list(raw_row["ingredients"]),
                "directions": _parse_list(raw_row["directions"]),
                "ner": _parse_list(raw_row["NER"]),
            }
            if not is_usable(row):
                continue

            storage.add_recipe({
                "title": row["title"],
                "ingredients": row["ingredients"],
                "ner": row["ner"],
                "steps": row["directions"],  # RecipeNLG calls this field "directions"; storage's schema calls it "steps"
                "cuisine": None,        # not in RecipeNLG; leave null for MVP
                "total_time": None,     # ditto
                "dietary_tags": [],     # ditto
            })
            count += 1
            if count % 1000 == 0:
                print(f"  seeded {count} (scanned {scanned})")

    print(f"done: seeded {count} usable recipes (scanned {scanned} to find them)")


if __name__ == "__main__":
    seed(5000)
