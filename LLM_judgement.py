from openai import OpenAI 
from config_api import get_openai_api_key

client = OpenAI(api_key=get_openai_api_key())

def llm_rank_courses(query, candidates):
    """
    candidates: List of dict with keys: id, title, description
    returns: top curated list of course dicts
    """
    items = [
        f"{c['id']}. {c['title']} - {c['description'][:80]}..."
        for c in candidates
    ]
    formatted = "\n".join(items)

    prompt = f"""
User query: "{query}"

Below is a list of course titles WITH DESCRIPTIONS.
Your job is:

1. REMOVE any course that is not truly relevant to the query
   (e.g., "singing" → remove video editing, NLP, devops, tableau, etc.)
2. REMOVE near-duplicate courses
3. ENSURE diversity of topics within the query
   (e.g., for "web development": include javascript, react, node)
4. RETURN ONLY the ranked IDs in order of relevance.
5. Max 10 items.

Courses:
{formatted}

Return answer strictly in JSON:
{{"ranked_ids": [3, 5, 7, ...]}}
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=200
    )

    import json
    try:
        ranked_ids = json.loads(resp.choices[0].message.content)["ranked_ids"]
    except:
        return candidates[:10]

    # Reorder candidates according to LLM output
    id_map = {c["id"]: c for c in candidates}
    final = []
    for rid in ranked_ids:
        if rid in id_map:
            final.append(id_map[rid])

    return final[:10]

















