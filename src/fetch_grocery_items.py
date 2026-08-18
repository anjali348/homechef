import pandas as pd
import json

df = pd.read_csv("data/grocerylist.csv")   # your actual filename
items = sorted({str(x).strip() for x in df["Item"].dropna()})

with open("data/grocery_items.json", "w") as f:
    json.dump(items, f)

print(f"saved {len(items)} grocery items")