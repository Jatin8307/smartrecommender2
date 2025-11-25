from LLM_judgement import get_llm_judgment

course = {
    "title": "Python Advanced Course",
    "description": "Learn decorators, OOP, threading, async programming."
}

keywords = ["python", "cloud"]

result = get_llm_judgment(course, keywords)
print("LLM result:", result)
