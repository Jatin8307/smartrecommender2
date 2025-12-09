import streamlit as st# type:ignore
from search_courses import get_sql_candidates
from rag_retriever_openai import retrieve_top_k_openai
from semantic_ranker import llm_infer_topic, llm_filter_and_rank

# STREAMLIT PAGE

st.set_page_config(
    page_title="Smart Course Recommender",
    layout="wide"
)

st.title("Smart Course Recommender")
st.write("Hybrid SQL + AI Semantic Search for Accurate Course Recommendations")

# USER INPUT

query_input = st.text_input(
    "Enter any topic, skill, domain, tool, or course name:",
    placeholder="e.g. web development, python backend, react, aws"
)

search_btn = st.button("Search Courses")

# BEGIN PIPELINE
if search_btn and query_input.strip():

    query = query_input.strip()
    st.write("Searching SQL database for exact matches...")
  
    # 1) SQL SEARCH
   
    sql_keywords = [k.lower() for k in query.replace(",", " ").split() if k.strip()]
    sql_results = get_sql_candidates(sql_keywords)

    if len(sql_results) > 0:
        st.success(f"Found {len(sql_results)} matching courses in SQL!")

        for i, course in enumerate(sql_results[:20], start=1):
            with st.container():
                st.markdown(f"### {i}. {course['title']}")
                st.write(course["description"])
                st.divider()

    else:
        st.warning("No direct SQL results found. Switching to AI semantic search...")

        # 2) OPENAI RAG RETRIEVAL
        with st.spinner("Retrieving semantically similar courses (RAG)..."):
            rag_candidates, rag_scores = retrieve_top_k_openai(query, k=80)

        if not rag_candidates:
            st.error("No semantically similar courses found in database.")
            st.stop()

        st.write(f"Retrieved **{len(rag_candidates)}** semantic candidates from embeddings.")

        # 3) LLM TOPIC INFERENCE
        with st.spinner("Understanding your query using AI..."):
            topic = llm_infer_topic(query, rag_candidates)

        st.write(f"**Detected Topic:** `{topic}`")

        if topic == "none":
            st.warning("AI could not determine a specific topic. Showing best semantic matches.")
            final_results = rag_candidates[:10]

        else:
            
            # 4) LLM FILTERING + RANKING
            
            with st.spinner("Filtering and re-ranking courses using AI..."):
                final_results = llm_filter_and_rank(query, topic, rag_candidates, max_output=10)

            if not final_results:
                st.error("No relevant courses found after AI filtering.")
                st.stop()

       
        # 5) DISPLAY FINAL RESULTS
       
        st.success("Top AI-Recommended Courses:")

        for i, course in enumerate(final_results, start=1):
            with st.container():
                st.markdown(f"### {i}. {course['title']}")
                st.write(course.get("description", ""))
                st.divider()

elif search_btn:
    st.warning("Please enter a search query before pressing Search.")
