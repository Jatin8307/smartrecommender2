import sqlite3, json, numpy as np
from openai import OpenAI
from config_api import get_openai_api_key
import os

client = OpenAI(api_key=get_openai_api_key())
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "courses.db")

def load_embeddings():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.title, c.description, e.embedding
        FROM courses c
        JOIN course_embeddings e ON c.id = e.course_id
    """)
    rows = cur.fetchall()
    conn.close()

    courses, vectors = [], []
    for cid, title, desc, emb in rows:
        courses.append({"id": cid, "title": title, "description": desc})
        vectors.append(json.loads(emb))

    return courses, np.array(vectors, dtype="float32")

_courses, _vectors = None, None

def get_index():
    global _courses, _vectors
    if _courses is None:
        _courses, _vectors = load_embeddings()
    return _courses, _vectors

def embed_query(text):
    r = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text]
    )
    return np.array(r.data[0].embedding)

def cosine_sim(q, m):
    q = q / np.linalg.norm(q)
    m = m / np.linalg.norm(m, axis=1, keepdims=True)
    return np.dot(m, q)

def retrieve_top_k(query, k=15):
    courses, vectors = get_index()
    q = embed_query(query)
    sims = cosine_sim(q, vectors)
    idxs = np.argsort(-sims)[:k]
    return [courses[i] for i in idxs]
