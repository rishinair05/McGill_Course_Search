import streamlit as st
import streamlit_analytics
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle
import pandas

encoder = SentenceTransformer("all-mpnet-base-v2")
#Importing index and datframe from pickles
with open('./FAISS_mcgill_courses_index.pkl', 'rb') as index_file:
    index = pickle.load(index_file)

with open('./mcgill_courses_dataframe.pkl', 'rb') as df_file:
    df = pickle.load(df_file)

course_code = df['Course Name']
description = df['Description']
department = df['Department']
course_terms = df['Terms']
course_instructors = df['Instructors']
course_prerequisites = df['Prerequisites']

def courseSearch(k_value, query):
    encoded_search_vector = np.array([encoder.encode(query)])
    faiss.normalize_L2(encoded_search_vector)
    distances, course_indices = index.search(encoded_search_vector, k=k_value)

    st.write("Here are " + str(number_of_results) + " courses that are semantically similar to your search query.")

    for i in range(k_value):       
        course_index = course_indices[0][i]
        st.write(str(course_code[course_index]))
        st.write(str(description[course_index]))
        st.write(str(department[course_index]))
        st.write(str(course_terms[course_index]))
        st.write((course_instructors[course_index]))
        st.write((course_prerequisites[course_index]))
        st.divider()

st.set_page_config(
    page_title = "McGill Semantic Course Search",
    layout="wide",
    initial_sidebar_state="auto"
)

#Sidebar
number_of_results = int(st.sidebar.number_input("Number of Results", min_value=1, value=10))
#Add filters for terms offered, subject/department, etc.

#Main Page
#st.image('./CoolLogo.png', width=200)

st.markdown(
    "<h1 style='text-align: center; '> The (Unofficial) McGill Course Searcher</h1>",
    unsafe_allow_html=True,
)

st.write("Disclaimer: This is not an official McGill tool. This software was developed\
          as a part of a research project on semantic/vector search engines by Rishi Nair (McGill '27). This search engine\
         uses the SBERT 'all-mpnet-base-v2' sentence transformer model, and the FAISS library developed by Facebook.")

st.write("You can enter your query as words or sentences. (e.g., 'Courses on Machine Learning', 'Newton's Method', 'Pizza', 'Metallica', etc.)")

st.write("Change the value on the left to return more or less search results.")

#Search Input
with streamlit_analytics.track(unsafe_password="#UDf2uFNDU$ud#bf"): #remove the password when uploading
    search_query = st.text_input("Enter a qeury to search courses", value="", max_chars=None, key=None, type="default")

#Search Output
if search_query != "":
    courseSearch(number_of_results, search_query)

st.caption("Author: Rishi Nair")
st.caption("Search Engine Analytics: http://localhost:8501/?analytics=on")