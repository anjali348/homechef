from fastapi import FastAPI
from pydantic import BaseModel
from src import pantry, qa, storage
import json
from pathlib import Path

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_grocery_path = Path(__file__).parent.parent / "data" / "grocery_items.json"
with open(_grocery_path) as f:
    GROCERY_ITEMS = json.load(f)   # loaded once at startup


# --- request models (define the shape of incoming data) ---
class PantryRequest(BaseModel):
    have: list[str]
    k: int = 10          # default if not provided

class AskRequest(BaseModel):
    question: str
    k: int = 4

class RecipeRequest(BaseModel):
    title: str
    ingredients: list[str] = []
    ner: list[str] = []
    steps: list[str] = []
    cuisine: str | None = None
    total_time: int | None = None
    dietary_tags: list[str] = []

# --- endpoints ---
@app.post("/pantry-match")
def pantry_match(req: PantryRequest):
    return pantry.match_pantry(req.have, k=req.k)

@app.post("/ask")
def ask(req: AskRequest):
    return qa.ask(req.question, k=req.k)

@app.get("/recipes")
def get_recipes():
    return storage.get_all_recipes()

@app.post("/recipes")
def create_recipe(req: RecipeRequest):
    recipe_id = storage.add_recipe(req.model_dump())
    return storage.get_recipe(recipe_id)

@app.get("/ingredients")
def get_ingredients():
    return GROCERY_ITEMS