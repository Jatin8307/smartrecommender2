# Local_rag_retriever.py
import sqlite3
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer#type:ignore
from sklearn.cluster import KMeans#type:ignore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "courses.db")
MODEL_NAME = "all-MiniLM-L6-v2"

# --- Configurable hyperparams ---
N_CLUSTERS = 12              # how many semantic clusters to build (tuneable)
MIN_SIMILARITY = 0.32        # basic threshold for candidate relevance (tuneable)
CANDIDATE_POOL_SIZE = 200    # number of top-similarity candidates to consider for clustering/quota
MAX_RESULTS = 10             # default k returned to UI
MAX_PER_CLUSTER_CAP = 0.5    # max fraction of final results any single cluster can occupy
TITLE_BOOST = 0.08           # additive boost to sim if title contains any query token
RANDOM_SEED = 42
STRICT_MIN_SIM = 0.40
# -------------------------------

model = SentenceTransformer(MODEL_NAME)

def load_index(with_clustering=True):
    """Load courses and embeddings from DB. Build clusters once."""
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
        raise ValueError(" NO EMBEDDINGS FOUND IN course_embeddings")

    courses = []
    vectors = []

    for cid, title, desc, emb in rows:
        courses.append({
            "id": cid,
            "title": title or "",
            "description": desc or ""
        })
        vectors.append(json.loads(emb))

    vectors = np.array(vectors, dtype="float32")

    # Build clustering (KMeans) once
    cluster_labels = None
    if with_clustering:
        # choose n_clusters <= number of samples
        n_clusters = min(N_CLUSTERS, len(vectors))
        # if too few items, assign single cluster
        if n_clusters <= 1:
            cluster_labels = np.zeros(len(vectors), dtype=int)
        else:
            kmeans = KMeans(n_clusters=n_clusters, random_state=RANDOM_SEED, n_init="auto")
            cluster_labels = kmeans.fit_predict(vectors)

    return courses, vectors, cluster_labels

# Lazy global cache
_COURSES = None
_VECTORS = None
_CLUSTER_LABELS = None

def get_index():
    global _COURSES, _VECTORS, _CLUSTER_LABELS
    if _COURSES is None:
        _COURSES, _VECTORS, _CLUSTER_LABELS = load_index()
    return _COURSES, _VECTORS, _CLUSTER_LABELS

def _normalize(vec):
    denom = np.linalg.norm(vec) + 1e-10
    return vec / denom

def _title_token_match_score(title, query_tokens):
    title_l = title.lower()
    for t in query_tokens:
        if t in title_l:
            return 1.0
    return 0.0

def retrieve_top_k(query, k=50):
    courses, vectors, cluster_labels = get_index()

    # EMBEDDING SIMILARITY (layer 1)
    q_vec = model.encode([query])[0].astype("float32")
    q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-10)
    v_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)

    sims = np.dot(v_norm, q_norm)

    # strict similarity cutoff
    STRICT_MIN_SIM = 0.40
    MODERATE_SIM = 0.32

    # First collect strong matches
    strong_idx = [i for i, s in enumerate(sims) if s >= STRICT_MIN_SIM]

    # If *no strong matches* → treat as "category not found"
    if len(strong_idx) == 0:
        return []  # Streamlit will show "no related courses"

    # If strong matches are too few, allow moderate ones
    moderate_idx = [i for i, s in enumerate(sims) if s >= MODERATE_SIM]

    candidate_idxs = list(dict.fromkeys(strong_idx + moderate_idx))
    candidate_idxs = candidate_idxs[:300]  # safety cap

    # HARD TOKEN FILTER (layer 2, mandatory)
    tokens = query.lower().split()

    def title_has_token(title):
        t = title.lower()
        return any(tok in t for tok in tokens)

    filtered = []
    for idx in candidate_idxs:
        title = courses[idx]["title"]
        desc = courses[idx]["description"]

        # Must match at least ONE token
        if title_has_token(title) or title_has_token(desc):
            filtered.append(idx)

    # if no filtered results → fallback to strong matches only
    if len(filtered) == 0:
        filtered = strong_idx.copy()

    # DIVERSIFICATION (layer 3)
    # Group by main keyword in title (javascript / react / node / aws / devops etc.)
    def primary_key(title):
        title = title.lower()
        for keyword in ["javascript", "react", "node", "frontend", "backend",
                        "python", "aws", "cloud", "devops", "nlp"]:
            if keyword in title:
                return keyword
        return title.split()[0]  # fallback
    
    buckets = {}
    for idx in filtered:
        key = primary_key(courses[idx]["title"])
        buckets.setdefault(key, []).append(idx)

    # pick max 2 from each bucket to ensure variety
    diversified = []
    for key, idxs in buckets.items():
        idxs_sorted = sorted(idxs, key=lambda i: sims[i], reverse=True)
        diversified.extend(idxs_sorted[:2])

    # sort final by score & remove duplicates
    diversified = sorted(list(dict.fromkeys(diversified)), key=lambda i: sims[i], reverse=True)

    # limit to k
    top = diversified[:k]

    # map to course dicts
    return [courses[i] for i in top]

