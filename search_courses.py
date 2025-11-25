import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "courses.db")
print("Using DB:", DB_PATH)
print("Exists:", os.path.exists(DB_PATH))


def get_sql_candidates(keywords):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
#debugging line
    # cursor.execute("SELECT COUNT(*) FROM courses;")
    # print("Total rows in courses table:", cursor.fetchone()[0])

    like_clauses = []
    params = []

    for kw in keywords:
        kw = kw.lower()
        pattern = f"%{kw}%"
        clause = "(LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(learning_objectives) LIKE ?)"
        like_clauses.append(clause)
        params.extend([pattern, pattern, pattern])

    where_clause = " OR ".join(like_clauses)

    query = f"""
        SELECT id, title, description
        FROM courses
        WHERE {where_clause};
    """

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results
