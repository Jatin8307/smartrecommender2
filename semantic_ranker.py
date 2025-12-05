# semantic_ranker.py
import json
from openai import OpenAI
from config_api import get_openai_api_key
import re

client = OpenAI(api_key=get_openai_api_key())
LLM_MODEL = "gpt-4o-mini"

def llm_infer_topic(query, candidates, max_preview=30):
    # prepare small candidate preview to help LLM infer topic
    preview = []
    for c in candidates[:max_preview]:
        preview.append(f"- {c['title']}: { (c['description'] or '')[:120] }")
    preview_text = "\n".join(preview)

    prompt = f"""
You are a helpful classifier. Given a user search query and a small set of candidate course titles and descriptions,
infer a short broad topic label that best represents the user's intent. Do NOT invent categories; use natural words.

Query:
{query}

Candidates:
{preview_text}

Return JSON only: {{ "topic": "<brief topic label or 'none'>" }}
"""
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role":"user","content":prompt}],
        max_tokens=40,
        temperature=0.0
    )
    text = resp.choices[0].message.content.strip()
    try:
        return json.loads(text)["topic"]
    except Exception:
        # best-effort fallback: extract a word if possible; else 'none'
        m = re.search(r'"topic"\s*:\s*"([^"]+)"', text)
        if m:
            return m.group(1)
        return "none"

def llm_filter_and_rank(query, topic, candidates, max_output=10):
    # Build compact candidate list to ask LLM to filter + rank
    items = []
    for c in candidates:
        short = (c.get("description") or "")[:120].replace("\n", " ")
        items.append(f"{c['id']}. {c['title']} -- {short}")

    items_text = "\n".join(items[:200])  # cap the context size

    prompt = f"""
User query: "{query}"
Inferred topic: "{topic}"

You are given a list of courses. Your job:
1) Remove any courses that are NOT relevant to the 'topic' above.
2) Remove near-duplicate courses (keep the best one).
3) Ensure good topical variety where appropriate.
4) Return at most {max_output} course IDs in ranked order (best first) as JSON:
{{"ranked_ids": [id1, id2, ...]}}

Courses:
{items_text}
"""

    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role":"user","content":prompt}],
        temperature=0.0,
        max_tokens=200
    )

    raw = resp.choices[0].message.content.strip()
    try:
        ranked = json.loads(raw)["ranked_ids"]
    except Exception:
        # robust parse: find integers in response
        ranked = [int(x) for x in re.findall(r"\d+", raw)] if raw else []

    id_map = {c["id"]: c for c in candidates}
    final = [id_map[i] for i in ranked if i in id_map]
    # fallback if LLM returned empty or invalid
    if not final:
        return candidates[:max_output]
    return final[:max_output]
