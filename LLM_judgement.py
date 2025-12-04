from openai import OpenAI 
from config_api import get_openai_api_key
import json

client = OpenAI(api_key=get_openai_api_key())

def rank_candidates_with_llm(query, candidates):
    """
    candidates = list of dicts with keys: id, title, description
    Returns reordered list by relevance.
    """

    lines = []
    for c in candidates:
        lines.append(f"{c['id']}. {c['title']}")

    prompt = f"""
User Query: {query}

Rank the most relevant courses from this list.
Return ONLY a JSON array of course IDs in best order.

Courses:
{chr(10).join(lines)}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Return only valid JSON. No explanation."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=80,
        temperature=0.0
    )

    try:
        ids = json.loads(response.choices[0].message.content)
        ranked = [c for cid in ids for c in candidates if c["id"] == cid]
        return ranked
    except:
        return candidates



















