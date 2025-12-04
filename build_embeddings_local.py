import sqlite3
import json, os
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "courses.db")
MODEL_NAME = "all-MiniLM-L6-v2" 

print("Loading local embedding model...")
model = SentenceTransformer(MODEL_NAME)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS course_embeddings (
    course_id INTEGER PRIMARY KEY,
    embedding TEXT
)
""")

# Only embed courses that are not already embedded
cur.execute("""
SELECT c.id, c.title, c.description
FROM courses c
LEFT JOIN course_embeddings e ON c.id = e.course_id
WHERE e.course_id IS NULL
""")

rows = cur.fetchall()
print(f"Remaining courses to embed: {len(rows)}")

BATCH_SIZE = 64

for i in range(0, len(rows), BATCH_SIZE):
    batch = rows[i:i+BATCH_SIZE]
    texts = [f"{r[1]} {r[2]}" for r in batch]

    print(f"Embedding batch {i+1} → {i+len(batch)}")

    embeddings = model.encode(texts).tolist()

    for (cid, _, _), emb in zip(batch, embeddings):
        cur.execute(
            "INSERT OR REPLACE INTO course_embeddings VALUES (?, ?)",
            (cid, json.dumps(emb))
        )

    conn.commit()

conn.close()
print("OFFLINE embeddings build complete.")
