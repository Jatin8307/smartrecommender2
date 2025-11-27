# LLM_judgment.py function use kar rha hai OpenAI to get relevance score from LLM
from openai import OpenAI
from config_api import get_openai_api_key
import re # for parsing integers

client = OpenAI(api_key=get_openai_api_key())

def get_llm_fallback_suggestions(keywords, categories, max_results=10):
    """
    Used ONLY when SQL returns 0 results.
    Returns a list of up to 10 course title suggestions.
    """

    keyword_text = ", ".join(keywords)
    category_text = ", ".join(categories)

    prompt = f"""
Keywords: {keyword_text}
Available Topics: {category_text}

Suggest up to {max_results} relevant COURSE TITLES only.
Return only a clean numbered list.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Return only course titles. No explanation."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=80,   # reduced from 120
        temperature=0.2
    )

    raw_text = response.choices[0].message.content.strip()

    suggestions = []
    for line in raw_text.split("\n"):
        line = line.strip().lstrip("0123456789.-• ").strip()
        if line:
            suggestions.append(line)

    return suggestions[:max_results]


# def get_llm_fallback_suggestions(keywords, categories, max_results=10):
#     """
#     Used ONLY when SQL returns 0 results.
#     Returns a list of up to 10 course title suggestions.
#     """

#     keyword_text = ", ".join(keywords)
#     category_text = ", ".join(categories)

#     prompt = f"""
# User searched for: {keyword_text}

# Available course categories in the platform:
# {category_text}

# Suggest up to {max_results} relevant COURSE TITLES only.
# Return only the titles as a bullet list.
# No explanation.
# """

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You suggest relevant course titles only."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=120
#     )

#     raw_text = response.choices[0].message.content.strip()

#     # Clean bullet list into Python list
#     suggestions = []
#     for line in raw_text.split("\n"):
#         line = line.strip().lstrip("-•").strip()
#         if line:
#             suggestions.append(line)

#     return suggestions[:max_results]















#_______________________________________________________________________________________________

# def parse_integer_score(text):
#     """
#     Parse an integer score between 1 and 10 from the model response text.
#     Accepts formats: "8", "8/10", "Score: 8", "8 out of 10", etc.
#     Returns int in [1,10]. If not parseable, returns None.
#     """
#     if text is None:
#         return None
#     # find first number 1-100
#     m = re.search(r"(\d{1,3})", text)
#     if not m:
#         return None
#     try:
#         val = int(m.group(1))
#     except ValueError:
#         return None
#     # clamp
#     if val < 1:
#         val = 1
#     if val > 10:
#         # if model returned percentage scale, map it to 1-10
#         if val <= 100:
#             # map 0-100 -> 1-10
#             val = max(1, min(10, round(val / 10)))
#         else:
#             val = 10
#     return val

# def get_llm_score(course_data, keywords, model="gpt-4o-mini", max_tokens=10):
#     """
#     Returns (score:int between 1-10, tokens_used:int).
#     If model response can't be parsed, returns score=1 (lowest) and tokens used as returned.
#     """
#     title = course_data.get("title", "")[:1000]   # truncate just in case
#     description = course_data.get("description", "")[:2000]
#     keyword_text = ", ".join(keywords)

#     prompt = f"""You are a strict evaluator. Given the user keywords and a course title+description,
# give a single numeric relevance score from 1 to 10 (1 = not relevant, 10 = perfect match).
# Return only the number (example: 8). Do NOT add any other text.
# Keywords: {keyword_text}
# Title: {title}
# Description: {description}
# """
#     response = client.chat.completions.create(
#         model=model,
#         messages=[
#             {"role": "system", "content": "You are a strict numeric relevance evaluator."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=max_tokens,  # small
#         temperature=0.0
#     )

#     # New SDK returns response.choices[0].message.content
#     answer_text = response.choices[0].message.content.strip()
#     score = parse_integer_score(answer_text)
#     tokens_used = getattr(response.usage, "total_tokens", None)
#     # Make safe defaults
#     if tokens_used is None:
#         # try dictionary access if SDK different
#         try:
#             tokens_used = response["usage"]["total_tokens"]
#         except Exception:
#             tokens_used = 0

#     if score is None:
#         # fallback: if parsing failed, treat as minimally relevant (1)
#         score = 1

#     return int(score), int(tokens_used)
