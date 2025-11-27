import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "courses.db")

def get_sql_candidates(keywords):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row    
    cursor = conn.cursor()

    like_clauses = []
    params = []

    for kw in keywords:
        kw = kw.lower()
        pattern = f"%{kw}%"
        clause = "(LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
        like_clauses.append(clause)
        params.extend([pattern, pattern])

    where_clause = " OR ".join(like_clauses)

    query = f"""
        SELECT id, title, description
        FROM courses
        WHERE {where_clause};
    """

    cursor.execute(query, params)
    rows = cursor.fetchall()  # these rows are now dict-like

    conn.close()

    # Convert row objects → pure Python dicts
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "title": r["title"],
            "description": r["description"]
        })

    return results



# Get distinct categories from the courses table,  prompt me use krne ke lie


#  $$ GLOBAL CACHE (memory me store hoga)
_CACHED_CATEGORIES = None
CACHE_FILE = "cached_categories.json"

def get_distinct_categories():
    """
    Permanent file-based cache.
    DB is hit only once ever.
    """

    # 1. If cache file exists → load it
    if os.path.exists(CACHE_FILE):
        print("Using FILE cached categories (no DB hit)")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Loading categories from DB (FIRST TIME EVER)...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT learning_objectives FROM courses;")
    rows = cursor.fetchall()
    conn.close()

    categories = []

    for r in rows:
        if r[0]:
            text = r[0].lower()

            if "python" in text:
                categories.append("Python")
            if "data" in text:
                categories.append("Data Science")
            if "machine learning" in text or "ml" in text:
                categories.append("Machine Learning")
            if "deep learning" in text:
                categories.append("Deep Learning")
            if "web" in text:
                categories.append("Web Development")
            if "sql" in text:
                categories.append("SQL")
            if "cloud" in text:
                categories.append("Cloud Computing")
            if "aws" in text:
                categories.append("AWS")
            if "devops" in text:
                categories.append("DevOps")

    categories = list(set(categories))

    # 2. SAVE to file so next time DB is never hit
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2)

    print("Categories cached permanently to file")

    return categories