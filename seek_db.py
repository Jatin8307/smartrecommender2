import sqlite3

DB_PATH = r"C:\Users\JatinKumar\Downloads\course_recommender\courses.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Print 10 sample rows
cursor.execute("SELECT id, title FROM courses LIMIT 10;")
rows = cursor.fetchall()

print("\n--- SAMPLE COURSES ---")
for r in rows:
    print(r)

# Print 10 random rows
cursor.execute("SELECT id, title FROM courses ORDER BY RANDOM() LIMIT 10;")
rows = cursor.fetchall()

print("\n--- RANDOM SAMPLE ---")
for r in rows:
    print(r)

conn.close()
