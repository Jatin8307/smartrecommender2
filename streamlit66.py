import streamlit as st # type:ignore
from search_courses import get_sql_candidates
from Local_rag_retriever import retrieve_top_k   # local model RAG

st.set_page_config(
    page_title="Smart Course Recommender (Local RAG)",
    layout="wide"
)

st.title("Smart Course Recommender (RAG Only)")
st.write("This version uses only SQL + Local Semantic Embeddings (MiniLM).")

# INPUT SECTION

query_input = st.text_input(
    "Search keywords:",
    placeholder="e.g. web development, python backend, react, aws"
)

search_btn = st.button("Search......")
# MAIN PIPELINE

if search_btn and query_input.strip():

    query = query_input.strip()
    st.write("Searching SQL database for direct matches...")

   
    # 1) SQL SEARCH
    
    sql_keywords = [k.lower() for k in query.replace(",", " ").split() if k.strip()]
    sql_results = get_sql_candidates(sql_keywords)

    if len(sql_results) > 0:
        st.success(f"Found {len(sql_results)} SQL matches.")
        st.write("### SQL Results:")
        
        for i, course in enumerate(sql_results[:20], start=1):
            with st.container():
                st.markdown(f"#### {i}. {course['title']}")
                st.write(course["description"])
                st.divider()

    else:
        st.warning("No SQL matches found. Switching to Local RAG retrieval...")

       
        # 2) LOCAL RAG SEARCH (local embedding model)
    
        with st.spinner("Retrieving semantic matches from local embeddings..."):
            local_results = retrieve_top_k(query, k=10)

        if len(local_results) == 0:
            st.error("No relevant semantic matches found using Local RAG.")
            st.stop()

        st.success(f"Found {len(local_results)} Local RAG results.")
        st.write("### Local RAG Results:")

        for i, course in enumerate(local_results, start=1):
            with st.container():
                st.markdown(f"#### {i}. {course['title']}")
                st.write(course.get("description", ""))
                st.divider()

elif search_btn:
    st.warning("Please enter a search query before searching.")
