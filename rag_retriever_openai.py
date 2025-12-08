import sqlite3
import json
import numpy as np
from openai import OpenAI
from config_api import get_openai_api_key
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "courses.db")
EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI(api_key=get_openai_api_key())

# cached in-memory copies
_COURSES = None
_VECTORS = None

def load_index():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.title, c.description, e.embedding
        FROM courses c
        JOIN course_embeddings e ON c.id = e.course_id
    """)
    rows = cur.fetchall()
    conn.close()

    courses = []
    vectors = []
    for cid, title, desc, emb_json in rows:
        courses.append({"id": cid, "title": title or "", "description": desc or ""})
        vectors.append(json.loads(emb_json))
    return courses, np.array(vectors, dtype="float32")

def get_index():
    global _COURSES, _VECTORS
    if _COURSES is None:
        _COURSES, _VECTORS = load_index()
        if len(_COURSES) == 0:
            raise RuntimeError("No stored OpenAI embeddings found - run build_openai_embeddings.py first.")
    return _COURSES, _VECTORS

def embed_query_openai(text):
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=[text])
    return np.array(resp.data[0].embedding, dtype="float32")

def cosine_sim(q, mat):
    # assume q shape (d,), mat shape (n,d)
    qn = q / (np.linalg.norm(q) + 1e-10)
    mn = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-10)
    return np.dot(mn, qn)

def retrieve_top_k_openai(query, k=50):
    courses, mat = get_index()
    q_vec = embed_query_openai(query)
    sims = cosine_sim(q_vec, mat)
    top_idx = np.argsort(-sims)[:k]
    return [courses[i] for i in top_idx], sims[top_idx]
