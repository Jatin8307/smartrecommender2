# SmartCourseRecommender
It uses SQL queries and LLM Intelligence to recommend the best possible course from a Database of 2000 online courses.


For semantic ranker over local rag, 
this will run using, streamlit_app77.py  --> command " streamlit run streamlt_app77.py"



basic guide to run the application
step 1: If you have a database, load that into folder,
step 2: create a python virtual environment if not thee, activate python virtual environment --> .venv/scripts/activate  
step 3: load your .env file and put the api key of your OpenAI account.
step 4: install all the requirements present in the requirements.txt file.
step 5: now run build_embeddings_loacl.py , it will create vector embeddings of your sql data inside the database.
step 6: Do not forget to add the database path which you will use.
step 7: Now run streamlit app.

streamlitapp.py ----> OpenAI pipeline with semantic filters
streamlit66.py ----> just local rag pipeline, no openAI involved, it used model = all-MiniLM-L6-v2
streamlit_app77.py ---> it used local rag pipeline, but uses a semantic LLM OPENAI filter to rank the output coming from local rag.