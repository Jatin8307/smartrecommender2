from openai import OpenAI 
from config_api import get_openai_api_key
import re

client = OpenAI(api_key=get_openai_api_key())

# chunks me todne ke lie 
def chunk_list(items, chunk_size):
    for i in range(0, len(items), chunk_size):
        yield items[i:i+chunk_size]


def get_llm_fallback_from_db_courses(keywords, all_courses, max_results=10, chunk_size=150):

    keyword_text = ", ".join(keywords)

    # Map title -> list of courses
    title_to_courses = {}
    for c in all_courses:
        title = (c["title"] or "").strip()
        if not title:
            continue
        title_to_courses.setdefault(title, []).append(c)

    selected_courses = []
    selected_titles = set()
    selected_ids = set()

    for chunk in chunk_list(all_courses, chunk_size):
        if len(selected_courses) >= max_results:
            break

        lines = []
        for idx, c in enumerate(chunk, start=1):
            t = (c["title"] or "").strip()
            if t:
                lines.append(f"{idx}. {t}")

        if not lines:
            continue

        titles_block = "\n".join(lines)

        prompt = f"""
User Keywords: {keyword_text}

From the following course titles, choose only those that are clearly relevant.
Return ONLY the titles, one per line, no extra text.

Course Titles:
{titles_block}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict filter. Only return titles that appear in the list. Do not invent new titles."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.0,
        )

        raw_text = response.choices[0].message.content.strip()

        for line in raw_text.split("\n"):
            clean = line.strip()
            clean = re.sub(r"^[0-9\.\)\-\s]+", "", clean).strip()

            if not clean:
                continue

            # TITLE LEVEL DEDUPLICATION
            if clean in selected_titles:
                continue

            if clean in title_to_courses:
                # Pick only ONE course for this title
                for course_obj in title_to_courses[clean]:
                    cid = course_obj["id"]

                    if cid not in selected_ids:
                        selected_courses.append(course_obj)
                        selected_titles.add(clean)
                        selected_ids.add(cid)
                        break   # VERY IMPORTANT: only ONE per title

            if len(selected_courses) >= max_results:
                break

    return selected_courses[:max_results]



















