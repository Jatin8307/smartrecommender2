import streamlit as st # type: ignore
from search_courses import get_sql_candidates, get_distinct_categories
from LLM_judgement import get_llm_fallback_suggestions

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

    # CASE 1: SQL FOUND RESULTS
    if len(sql_results) > 0:
        st.success(f" {len(sql_results)} courses found")
        st.write("Matching Courses:")

        for i, course in enumerate(sql_results[:20], start=1):
            with st.container():
                st.markdown(f"### {i}. {course['title']}")
                st.write(course["description"])
                st.divider()

    # CASE 2: SQL FOUND NOTHING → LLM FALLBACK
    else:
        # st.warning("No direct match found in database.")
        st.info("AI fallback suggestions...")

        categories = get_distinct_categories()

        with st.spinner("AI is generating course suggestions..."):
            suggestions = get_llm_fallback_suggestions(keywords, categories, max_results=10)

        st.success("AI Suggested Courses:")
        for i, title in enumerate(suggestions, start=1):
            st.markdown(f"**{i}. {title}**")

elif search_button:
    st.warning("Please enter some keywords.")

