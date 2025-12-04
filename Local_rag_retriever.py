import sqlite3
import json, os
import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "courses.db")
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

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

    if not rows:
        raise ValueError("NO EMBEDDINGS FOUND IN course_embeddings")

    courses = []
    vectors = []

    for cid, title, desc, emb in rows:
        courses.append({
            "id": cid,
            "title": title,
            "description": desc
        })
        vectors.append(json.loads(emb))

    return courses, np.array(vectors, dtype="float32")

_COURSES = None
_VECTORS = None

def get_index():
    global _COURSES, _VECTORS
    if _COURSES is None:
        _COURSES, _VECTORS = load_index()
    return _COURSES, _VECTORS

def retrieve_top_k(query, k=10):
    courses, vectors = get_index()

    q_vec = model.encode([query])[0].astype("float32")

    q_norm = q_vec / np.linalg.norm(q_vec)
    v_norm = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    sims = np.dot(v_norm, q_norm)
    top_idx = np.argsort(-sims)[:k]

    return [courses[i] for i in top_idx]
