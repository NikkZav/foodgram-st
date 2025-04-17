import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'ingredients.json'), encoding='utf-8') as f:
    raw = json.load(f)

formatted = [
    {"model": "recipes.ingredient", "fields": item}
    for item in raw
]

with open(os.path.join(BASE_DIR, 'db_ingredients.json'), 'w', encoding='utf-8') as f:
    json.dump(formatted, f, ensure_ascii=False, indent=2)
