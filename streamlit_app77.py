import streamlit as st #type:ignore
from search_courses import get_sql_candidates
from Local_rag_retriever import retrieve_top_k
from semantic_ranker import llm_infer_topic, llm_filter_and_rank

st.set_page_config(
    page_title="Smart Course Recommender (Local RAG + Ranker)",
    layout="wide"
)

st.title("Smart Course Recommender")
st.write("SQL → Local RAG → Semantic Ranking → Final Top 15")

query_input = st.text_input(
    "Search keywords:",
    placeholder="e.g. web development, python backend, react, aws"
)

search_btn = st.button("Search......")

if search_btn and query_input.strip():

    query = query_input.strip()
    # 1. SQL SEARCH
    
    st.write("Searching SQL database for direct matches...")
    sql_keywords = [k.lower() for k in query.replace(",", " ").split() if k.strip()]
    sql_results = get_sql_candidates(sql_keywords)

    candidates = []

    if len(sql_results) > 0:
        st.success(f"Found {len(sql_results)} SQL matches.")
        st.write("### SQL Results (Raw):")

        for i, c in enumerate(sql_results[:20], start=1):
            st.markdown(f"#### {i}. {c['title']}")
            st.write(c["description"])
            st.divider()

        # Use only SQL results as RAG candidates
        candidates = sql_results

    else:
      
        # 2. LOCAL RAG SEARCH
        st.warning("No SQL matches found. Switching to Local RAG retrieval...")

        with st.spinner("Retrieving semantic matches from local embeddings..."):
            local_results = retrieve_top_k(query, k=35)

        if len(local_results) == 0:
            st.error("No relevant semantic matches from Local RAG.")
            st.stop()

        st.success(f"Found {len(local_results)} Local RAG results.")
        st.write("### Local RAG Results (Raw):")

        for i, c in enumerate(local_results, start=1):
            st.markdown(f"#### {i}. {c['title']}")
            st.write(c.get("description", ""))
            st.divider()

        candidates = local_results

    # 3. SEMANTIC RANKING by LLM ranker
    st.subheader("Ranking candidates using Semantic Ranker...")

    # Step 1: infer topic
    with st.spinner("Inferring topic..."):
        topic = llm_infer_topic(query, candidates)

    st.info(f"Inferred Topic: **{topic}**")

    # Step 2: LLM filtering + ranking
    with st.spinner("Filtering & ranking best matches..."):
        ranked_results = llm_filter_and_rank(
            query=query,
            topic=topic,
            candidates=candidates,
            max_output=15,
        )

    st.success(f"Final Top {len(ranked_results)} Ranked Courses:")

    # 4. SHOW USEFUL TOP 15 COURSES
    for i, c in enumerate(ranked_results, start=1):
        st.markdown(f"### {i}. {c['title']}")
        st.write(c.get("description", ""))
        st.caption(f"Course ID: {c['id']}")
        st.divider()

elif search_btn:
    st.warning("Please enter a search query.")
