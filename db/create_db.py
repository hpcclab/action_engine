"""
This file creates a function vector database from the original API information list.
Specifically, using FAISS with an OpenAI embedding model ("text-embedding-3-large"),
we vectorize the summarized description of each function for further Top-k function selection.
"""

import pandas as pd
import numpy as np
import os
import time
import pickle
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

path = "./db/api_info/"
passage_data = pd.read_csv(path + "api_information.csv")
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = openai_api_key

embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")

start = time.time()
metadatas = []
for index, row in passage_data.iterrows():
    doc_meta = {
        "id": row['Id'],
        "name": row['name'],
    }
    metadatas.append(doc_meta)

faiss = FAISS.from_texts(passage_data['summary'].tolist(), embedding_function, metadatas)
print("Time Taken --> ", time.time()-start) 

faiss.save_local(path + 'vectordb/LangChain_FAISS', "api_vec")