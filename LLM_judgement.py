from openai import OpenAI
from config_api import get_openai_api_key
# yahan se openai ki api key milegi

client = OpenAI(api_key=get_openai_api_key())
# yahan se openai ka client banega

# har course ke liye ye function call hoga is function ki help se
def get_llm_judgment(course_data, keywords):
    """
    Evaluate if a single course is relevant to the given keywords.
    Returns "YES" or "NO".
    """

    title = course_data.get("title", "")
    description = course_data.get("description", "")
    keyword_text = ", ".join(keywords)

    prompt = f"""
Keywords: {keyword_text}
Course Title: {title}
Course Description: {description}

Does this course clearly teach or provide guidance to learn these keywords?
Reply strictly with YES or NO only.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Lightweight, fast, low cost
        messages=[
            {"role": "system", "content": "You are a strict relevance evaluator."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=5
    )

    answer = response.choices[0].message.content.strip().upper()
# answer me strip matlab spaces hata dena aur upper matlab sab capital letters me kar dena

    if "YES" in answer:
        return "YES"
    return "NO"
