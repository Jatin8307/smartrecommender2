from search_courses import get_sql_candidates, get_all_courses
from LLM_judgement import get_llm_fallback_from_db_courses
import argparse

def main():
    parser = argparse.ArgumentParser(description="SQL First + LLM Fallback Search")
    parser.add_argument("--keywords", "-k", type=str, required=True, help="Search keywords")
    args = parser.parse_args()

    raw = args.keywords.replace(",", " ")
    keywords = [k.strip().lower() for k in raw.split() if k.strip()]

    print("\n Searching with SQL for:", keywords)
    sql_results = get_sql_candidates(keywords)

    # CASE 1 — SQL FOUND RESULTS → SHOW DIRECTLY
    if len(sql_results) > 0:
        print(f"\n {len(sql_results)} results found from database:\n")

        for i, course in enumerate(sql_results[:20], start=1):
            print(f"{i}. {course['title']}")

        return

    # CASE 2 — SQL FOUND NOTHING → ACTIVATE DB-ONLY LLM FALLBACK
    else:
        print("\nNo direct match found in database.")
        print("AI fallback suggestions from DB courses...\n")

        all_courses = get_all_courses()
        suggestions = get_llm_fallback_from_db_courses(
            keywords,
            all_courses,
            max_results=10,
            chunk_size=150
        )

        print("\n AI Suggested Courses (from DB only):\n")
        for i, course in enumerate(suggestions, start=1):
            print(f"{i}. {course['title']} (id={course['id']})")


if __name__ == "__main__":
    main()


#-----------------------------------------------------------------------------------------------
# import time
# import argparse
# from search_courses import get_sql_candidates
# from LLM_judgement import get_llm_score
# import math

# # small delay between LLM calls to be polite / avoid rate-limits
# LLM_DELAY_SECONDS = 0.18  # adjust if you hit rate limits


# def run_pipeline(keywords, top_k=20, use_sleep=True):
#     """
#     Orchestrates SQL -> LLM scoring -> ranking.
#     Returns ranked list of dicts with fields: id, title, description, score
#     Also returns token stats.
#     """
#     print("Running SQL candidate search for keywords:", keywords)
#     sql_rows = get_sql_candidates(keywords)
#     total_sql = len(sql_rows)
#     print(f"Stage 1 (SQL) candidates found: {total_sql}")

#     scored_results = []
#     total_tokens = 0
#     llm_calls = 0

#     for i, course in enumerate(sql_rows, start=1):
#         print(f"[{i}/{total_sql}] Evaluating: id={course.get('id')} title={course.get('title')[:60]}")
        
#         score, tokens_used = get_llm_score(course, keywords)
#         total_tokens += tokens_used
#         llm_calls += 1
        
#         scored_results.append({
#             "id": course.get("id"),
#             "title": course.get("title"),
#             "description": course.get("description"),
#             "score": score,
#             "tokens": tokens_used
#         })
#         # sleep small amount to avoid strict rate limits
#         if use_sleep and LLM_DELAY_SECONDS > 0:
#             time.sleep(LLM_DELAY_SECONDS)

#     # sort by score descending, then tokens ascending
#     scored_results.sort(key=lambda x: (-x["score"], x["tokens"]))

#     print("\n=== LLM Scoring Summary ===")
#     print(f"Total SQL candidates evaluated: {total_sql}")
#     print(f"LLM calls made: {llm_calls}")
#     print(f"Total tokens used: {total_tokens}")
#     avg = (total_tokens / llm_calls) if llm_calls else 0
#     print(f"Average tokens per call: {avg:.2f}")

#     # return top ranked results
#     return scored_results[:top_k], {"total_candidates": total_sql, "llm_calls": llm_calls, "total_tokens": total_tokens, "avg_tokens": avg}

# def pretty_print_results(results):
#     print("\n=== TOP RESULTS ===")
#     for idx, r in enumerate(results, start=1):
#         print(f"{idx}. [{r['score']}] {r['title']} (id={r['id']}) - tokens={r['tokens']}")
#         # short description
#         desc = r.get("description", "")
#         if desc:
#             print("    ", desc[:220].replace("\n", " "), "...")
#     print("")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Run SQL->LLM pipeline and rank courses.")
#     parser.add_argument("--keywords", "-k", type=str, required=True, help="Comma or space-separated keywords")
#     parser.add_argument("--topk", "-n", type=int, default=20, help="Number of top results to display")
#     args = parser.parse_args()

#     # normalize keywords input
#     raw = args.keywords.replace(",", " ")
#     keywords = [k.strip().lower() for k in raw.split() if k.strip()]

#     results, stats = run_pipeline(keywords, top_k=args.topk)
#     pretty_print_results(results)
