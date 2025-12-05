import sqlite3
import json
import time
from openai import OpenAI
from config_api import get_openai_api_key
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "courses.db")
BATCH_SIZE = 50
EMBEDDING_MODEL = "text-embedding-3-small"  # cost-efficient and good quality
RETRY_BASE = 1.0
MAX_RETRIES = 5

client = OpenAI(api_key=get_openai_api_key())

def ensure_table(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS course_embeddings (
        course_id INTEGER PRIMARY KEY,
        embedding TEXT
    )
    """)
    conn.commit()

def get_unembedded_rows(conn):
    cur = conn.cursor()
    cur.execute("""
      SELECT c.id, c.title, c.description
      FROM courses c
      LEFT JOIN course_embeddings e ON c.id = e.course_id
      WHERE e.course_id IS NULL
    """)
    return cur.fetchall()

def embed_texts(texts):
    # inputs list of strings -> returns list of vectors
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
            return [d.embedding for d in resp.data]
        except Exception as e:
            wait = RETRY_BASE * (2 ** attempt)
            print(f"Embedding API error (attempt {attempt+1}): {e}. Retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError("Embedding API failed after retries")

def main():
    conn = sqlite3.connect(DB_PATH)
    ensure_table(conn)
    rows = get_unembedded_rows(conn)
    print("Remaining to embed:", len(rows))
    if not rows:
        print("Nothing to embed. Exiting.")
        conn.close()
        return

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i+BATCH_SIZE]
        texts = [f"{r[1]} {r[2] or ''}" for r in batch]
        print(f"Embedding batch {i+1} -> {i+len(batch)} (size {len(batch)})")
        try:
            embeddings = embed_texts(texts)
        except Exception as e:
            print("Fatal embedding error:", e)
            print("Stop. Re-run script later to resume.")
            break

        cur = conn.cursor()
        for (course_row, emb) in zip(batch, embeddings):
            cid = course_row[0]
            cur.execute(
                "INSERT OR REPLACE INTO course_embeddings (course_id, embedding) VALUES (?, ?)",
                (cid, json.dumps(emb))
            )
        conn.commit()
        # gentle pause so you don't burst limits
        time.sleep(1.0)

    conn.close()
    print("Embedding build complete.")

if __name__ == "__main__":
    main()
