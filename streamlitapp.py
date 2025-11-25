import streamlit as st
from search_courses import get_sql_candidates

st.title("Course Recommender Service")

keywords = st.text_input("Hey, Enter course you are looking for today! (comma separated)")

if st.button("Search"):
    # Allow user to enter keywords separated by comma OR space
    raw = keywords.replace(",", " ")
    kw_list = [k.strip().lower() for k in raw.split() if k.strip()]

    results = get_sql_candidates(kw_list)

    st.write(f"Found {len(results)} courses:")
    for r in results[:50]:
        st.write(r)
