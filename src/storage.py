"""
storage.py — structured recipe storage in SQLite.

Note the user_id column: it's always 'local' for now, but its presence
means multi-user accounts drop in later WITHOUT a schema rewrite.

"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "recipes.db"


# Opens a fresh connection, creates the recipes table if missing, then
# closes it. Safe to call on every startup since CREATE TABLE IF NOT EXISTS
# is a no-op once the schema already exists.
def init_db():
    """Create the recipes table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      TEXT NOT NULL DEFAULT 'local',
            title        TEXT NOT NULL,
            ingredients  TEXT NOT NULL,   -- JSON list of raw strings
            ner          TEXT,            -- JSON list of core ingredient names
            steps        TEXT,            -- JSON list of step strings
            cuisine      TEXT,
            total_time   INTEGER,         -- minutes, nullable
            dietary_tags TEXT             -- JSON list, e.g. ["vegan","gluten-free"]
        )
    """)
    conn.commit()
    conn.close()


# Serializes the list/dict fields to JSON text (SQLite has no native list
# type) and inserts a single row. Missing optional keys fall back to
# empty lists/None rather than raising, so callers can pass partial recipes.
def add_recipe(recipe: dict, user_id: str = "local") -> int:
    """
    Insert one recipe. `recipe` keys: title, ingredients (list), ner (list),
    steps (list), cuisine (str|None), total_time (int|None), dietary_tags (list).
    Returns the new row id.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        """INSERT INTO recipes
           (user_id, title, ingredients, ner, steps, cuisine, total_time, dietary_tags)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id,
            recipe["title"],
            json.dumps(recipe.get("ingredients", [])),
            json.dumps(recipe.get("ner", [])),
            json.dumps(recipe.get("steps", [])),
            recipe.get("cuisine"),
            recipe.get("total_time"),
            json.dumps(recipe.get("dietary_tags", [])),
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


# Converts a raw sqlite3 row tuple (column order matches the CREATE TABLE
# statement above) back into the dict shape callers work with, decoding
# the JSON-encoded columns and defaulting nullable ones to empty lists.
def _row_to_dict(row) -> dict:
    return {
        "id": row[0],
        "user_id": row[1],
        "title": row[2],
        "ingredients": json.loads(row[3]),
        "ner": json.loads(row[4]) if row[4] else [],
        "steps": json.loads(row[5]) if row[5] else [],
        "cuisine": row[6],
        "total_time": row[7],
        "dietary_tags": json.loads(row[8]) if row[8] else [],
    }


# Fetches a single recipe by primary key. Returns None instead of raising
# when no row matches, so callers can use a simple truthiness check.
def get_recipe(recipe_id: int) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


# Loads every recipe into memory. Fine at small scale (this is a
# single-user local tool); revisit with pagination/filtering if the
# table grows large enough for this to become a bottleneck.
def get_all_recipes() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM recipes").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


if __name__ == "__main__":
    # Quick self-test
    init_db()
    rid = add_recipe({
        "title": "Chocolate Milk",
        "ingredients": ["1 ml flour", "2 eggs", "1 c. milk"],
        "ner": ["flour", "eggs", "milk"],
        "steps": ["Mix.", "Cook."],
        "cuisine": "American",
        "total_time": 20,
        "dietary_tags": ["vegetarian"],
    })
    print("inserted id:", rid)
    print("read back:", get_recipe(rid))
