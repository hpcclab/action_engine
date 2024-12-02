"""
This file creates function vector databese from original API infomation list
Specifically, using FAISS with all-MiniLM-L6-L2 we vectorize summarized decription of each function 
for further Top-k function selection
"""

from langchain_community.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings

import pandas as pd
import numpy as np
import os
import time
import pickle

path = "/home/cc/AutomaticWorkflowGeneration/ActionEngine/db/api_info/"
passage_data = pd.read_csv(path + "api_information.csv")

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

start=time.time()
metadatas = []
for index, row in passage_data.iterrows():
    doc_meta = {
        "id": row['Id'],
        "name": row['name'],
        "category": row['category']
    }
    metadatas.append(doc_meta)

faiss = FAISS.from_texts(passage_data['summary'].tolist(), embedding_function, metadatas)
print("Time Taken --> ", time.time()-start) 

faiss.save_local(path + 'vectordb/LangChain_FAISS', "api_vec")
