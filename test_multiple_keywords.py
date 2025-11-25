from LLM_judgement import get_llm_judgment

# Multiple test cases
tests = [
    {
        "course": {
            "title": "Python Advanced Course",
            "description": "Learn decorators, OOP, threading, async programming."
        },
        "keywords": ["python"]
    },
    {
        "course": {
            "title": "Python Advanced Course",
            "description": "Learn decorators, OOP, threading, async programming."
        },
        "keywords": ["machine learning"]
    },
    {
        "course": {
            "title": "Cloud Computing Professional Course",
            "description": "This course teaches AWS, Azure, and GCP fundamentals."
        },
        "keywords": ["cloud", "aws"]
    },
    {
        "course": {
            "title": "Leadership Training Program",
            "description": "Learn communication, team management, and leadership."
        },
        "keywords": ["python", "cloud"]
    }
]

# Run all cases
for idx, test in enumerate(tests, start=1):
    print(f"\n--- Test Case {idx} ---")
    print("Keywords:", test["keywords"])
    print("Course Title:", test["course"]["title"])
    result = get_llm_judgment(test["course"], test["keywords"])
    print("LLM Result:", result)
