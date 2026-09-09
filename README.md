# Recipe Assistant
 
Tell it what's in your kitchen and it ranks what you can cook, or ask it questions answered from the recipe collection with citations.
 
## Stack
 
Backend is FastAPI (Python). Recipes live in SQLite. Recipe embeddings live in ChromaDB. Embeddings are made with sentence-transformers, and the Q&A answers come from the Anthropic API. Frontend is Next.js.
 
## Files
 
**Backend (`src/`)**
 
- `storage.py` — defines the SQLite recipe schema and the functions to add and read recipes.
- `normalize.py` — parses messy ingredient text and decides when two ingredient names mean the same thing.
- `embeddings.py` — turns recipes into vectors and runs semantic search over them.
- `pantry.py` — matches a user's ingredients against recipes and ranks them.
- `qa.py` — the RAG logic: finds relevant recipes and has the LLM answer from them.
- `api.py` — exposes the above as HTTP endpoints.
- `seed.py` — loads the recipe dataset into the database.
**Frontend (`app/`)**
 
- `page.js` — the pantry view.
- `chat/page.js` — the Q&A view.
- `add/page.js` — the add-recipe form.
- `layout.js` — shared nav across the pages.
## Features
 
**Pantry match.** You enter the ingredients you have. It checks each recipe, figures out what you're missing, and ranks recipes by how few ingredients you'd still need to buy. Uses fuzzy matching so "chicken" counts for "chicken breast."
 
**Recipe Q&A.** You ask a question in plain English. It finds the most relevant recipes, gives them to the LLM as context, and returns an answer that cites which recipes it used. The answer comes from the recipe collection, not the model's general knowledge.
 
**Add a recipe.** You fill in a title, ingredients, and steps. The recipe is saved and immediately works in pantry match and Q&A alongside the seed data.
 
## Scaling to a bigger dataset
 
Right now the app loads 5,000 recipes. That's a choice for development speed, not a limit of the design — the full RecipeNLG dataset is about 2 million recipes. Loading more is mostly a matter of changing one number in `seed.py`, but a few parts of the pipeline would need to change to handle that scale:
 
- **Seeding.** SQLite handles millions of rows fine. The main fix is batching the inserts into fewer transactions so the load doesn't crawl.
- **Embedding.** Turning 2M recipes into vectors is slow on a CPU. This is the real bottleneck — it would need a GPU and the job made resumable so a crash partway through doesn't mean starting over.
- **Vector store.** ChromaDB running locally is fine for tens of thousands of vectors but strains near millions. At that scale I'd move to a vector database built for it — Qdrant, Weaviate, or Postgres with pgvector.
- **Pantry matching.** This is the part that quietly breaks. Right now it scans every recipe for each query, which is fine at 5,000 and far too slow at 2M. The fix is an inverted index — a lookup from each ingredient to the recipes that contain it — so a query does fast set lookups instead of a full scan.
Some of these are solved by better hardware or tools (embedding, the vector store) and some need a different approach (the inverted index for pantry matching).
 
## To be added
 
- User login and saved pantries.
- A cleaner, more polished UI.
- Demo video (coming soon).
- Evaluation metrics for the RAG answers (relevance, groundedness, and whether sources actually support the answer).
 
