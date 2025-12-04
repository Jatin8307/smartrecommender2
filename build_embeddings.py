import sqlite3, json, time, os
from openai import OpenAI
from config_api import get_openai_api_key

BATCH_SIZE = 50   
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "courses.db")

client = OpenAI(api_key=get_openai_api_key())

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS course_embeddings (
    course_id INTEGER PRIMARY KEY,
    embedding TEXT
)
""")

cur.execute("""
SELECT c.id, c.title, c.description
FROM courses c
LEFT JOIN course_embeddings e ON c.id = e.course_id
WHERE e.course_id IS NULL
""")

rows = cur.fetchall()
print(f"Remaining courses to embed: {len(rows)}")

for i in range(0, len(rows), BATCH_SIZE):
    batch = rows[i:i+BATCH_SIZE]
    texts = [f"{r[1]} {r[2]}" for r in batch]

    print(f"Embedding batch {i+1} → {i+len(batch)}")

    try:
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
    except Exception as e:
        print("Error:", e)
        print("Stopping safely. You can re-run this script.")
        break

    for (cid, _, _), emb in zip(batch, resp.data):
        cur.execute(
            "INSERT OR REPLACE INTO course_embeddings VALUES (?, ?)",
            (cid, json.dumps(emb.embedding))
        )

    conn.commit()
    time.sleep(2) 

conn.close()
print("Embedding build complete.")
