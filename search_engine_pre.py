import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import pickle

#Open dataframe containing information on all mcgill courses
with open('./mcgill_courses_dataframe.pkl', 'rb') as df_file:
    df = pickle.load(df_file)

#Encode the course descriptions into vectors using SBERT "all-mpnet-base-v2" model.
description = df['Course Name'] + " " + df['Description']
encoder = SentenceTransformer("all-mpnet-base-v2")
encoded_vectors = encoder.encode(description)

#Create an FAISS index.
d = encoded_vectors.shape[1]
index = faiss.IndexFlatIP(d)
faiss.normalize_L2(encoded_vectors)
index.add(encoded_vectors)

#Store FAISS index as a pickle.
FAISS_index_file_name = 'FAISS_mcgill_courses_index.pkl'
with open(FAISS_index_file_name, 'wb') as file:
    pickle.dump(index, file)
    print("FAISS Index successfully saved to " + FAISS_index_file_name)