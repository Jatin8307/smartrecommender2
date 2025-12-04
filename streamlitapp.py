import streamlit as st  # type: ignore
from search_courses import get_sql_candidates
from Local_rag_retriever import retrieve_top_k  

st.set_page_config(page_title="Smart Course Recommender", layout="wide")

st.title("Smart Course Recommender")
st.write("SQL-based search with AI fallback")

keywords_input = st.text_input(
    "Please Enter course name:",
    placeholder="e.g. python machine learning, blockchain, physics"
)

search_button = st.button("Search Courses")

if search_button and keywords_input.strip():

    raw = keywords_input.replace(",", " ")
    keywords = [k.strip().lower() for k in raw.split() if k.strip()]

    st.write("Searching database...")
    sql_results = get_sql_candidates(keywords)

    # CASE 1 — SQL FOUND RESULTS
    if len(sql_results) > 0:
        st.success(f"{len(sql_results)} courses found")
        st.write("Matching Courses:")

        for i, course in enumerate(sql_results[:20], start=1):
            with st.container():
                st.markdown(f"### {i}. {course['title']}")
                st.write(course["description"])
                st.divider()

    # CASE 2 — OFFLINE RAG FALLBACK (FINAL, CLEAN)
    else:
        st.warning("No direct match found with SQL in the database.")

        with st.spinner("Finding relevant courses using Offline AI..."):
            try:
                st.write(" Offline RAG module loaded")

                query_text = " ".join(keywords)
                suggestions = retrieve_top_k(query_text, k=10)

                st.write(f"Retrieved {len(suggestions)} results from RAG")

            except Exception as e:
                st.error("RAG FAILED")
                st.exception(e)
                suggestions = []

        if suggestions:
            st.success("AI Suggested Courses:")

            for i, course in enumerate(suggestions, start=1):
                with st.container():
                    st.markdown(f"### {i}. {course['title']}")
                    if course.get("description"):
                        st.write(course["description"])
                    st.divider()
        else:
            st.error("RAG returned zero results.")

elif search_button:
    st.warning("Please enter some keywords.")
