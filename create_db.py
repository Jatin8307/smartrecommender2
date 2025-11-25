import sqlite3
import random

def create_database():
    conn = sqlite3.connect("courses.db")
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            learning_objectives TEXT
        );
    """)

    # Keyword pools for random generation
    subjects = [
        "Python", "Java", "C++", "JavaScript", "React", "Node.js", "Django", "Flask",
        "Machine Learning", "Deep Learning", "AI", "NLP", "Data Science",
        "SQL", "Power BI", "Tableau", "Cloud Computing", "AWS", "Azure", "GCP",
        "Cybersecurity", "DevOps", "Docker", "Kubernetes",
        "Business Analytics", "Finance", "Marketing", "Sales Strategy",
        "Graphic Design", "UI/UX", "Animation", "Video Editing",
        "Leadership", "Communication Skills", "Time Management"
    ]

    levels = [
        "Beginner", "Intermediate", "Advanced", "Professional", "Masterclass"
    ]

    verbs = [
        "Learn", "Understand", "Master", "Explore", "Build", "Create", "Develop", "Implement"
    ]

    topics = [
        "real-world applications", "industry projects", "hands-on coding",
        "problem-solving skills", "business use cases", "cloud deployment",
        "data pipelines", "automation workflows", "best practices"
    ]

    mock_courses = []

    for i in range(2000):
        subject = random.choice(subjects)
        level = random.choice(levels)

        title = f"{subject} {level} Course"

        description = (
            f"This is a {level.lower()} level course on {subject}. "
            f"It covers practical techniques and {random.choice(topics)}."
        )

        learning_objectives = (
            f"{random.choice(verbs)} {subject}; "
            f"{random.choice(verbs)} advanced concepts; "
            f"Apply skills to {random.choice(topics)}."
        )

        mock_courses.append((title, description, learning_objectives))

    # Insert data in bulk
    cursor.executemany("""
        INSERT INTO courses (title, description, learning_objectives)
        VALUES (?, ?, ?);
    """, mock_courses)

    conn.commit()
    conn.close()
    print("Database created with 2000+ mock courses.")

if __name__ == "__main__":
    create_database()
