import json
from outlines import models, generate
import sqlite3

from foudinge.entities import Summary, prompt_template

# load model
# model = models.mlxlm("mlx-community/Meta-Llama-3.1-8B-Instruct-8bit")
model = models.openai("gpt-4o-mini")
generator = generate.json(model, Summary)

db_name = "reviews.db"


with sqlite3.connect(db_name) as conn:
    c = conn.cursor()
    data = c.execute(f"SELECT url, title, review FROM reviews").fetchall()

with sqlite3.connect(db_name) as conn:
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS inferred_entities_openai(url TEXT PRIMARY KEY, entities TEXT)"
    )

with sqlite3.connect(db_name) as conn:
    c = conn.cursor()
    c.execute("SELECT url FROM inferred_entities_openai")
    existing_urls = set(row[0] for row in c.fetchall())


for url, title, text in data:
    if url not in existing_urls:
        print(f"Result: {title} (https://lefooding.com{url})\n")
        print(f"{text}\n")
        if (
            url != "/restaurants/oiseau-oiseau"
            and url != "/restaurants/le-petit-hibou"
            and url != "/restaurants/roots"
            and url != "/restaurants/restaurant-l-esprit-du-causse-concots-3"
            and url != "/restaurants/popote"
        ):
            result = generator(
                prompt_template(text, json.dumps(Summary.model_json_schema(), indent=2))
            )
            print(*result.people, sep="\n")
            c.execute(
                """
                INSERT INTO inferred_entities_openai(url, entities)
                VALUES(?, ?)
                ON CONFLICT(url)
                DO UPDATE SET
                    entities=excluded.entities
            """,
                (url, json.dumps(result.model_dump())),
            )
            conn.commit()
    else:
        print(f"Already inferred: {title} ({url})")
