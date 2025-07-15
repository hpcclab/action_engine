"""
This file creates a function vector database from the original API information list.
Specifically, using FAISS with an OpenAI embedding model ("text-embedding-3-large"),
we vectorize the summarized description of each function for further Top-k function selection.
"""

import json
import pandas as pd
import numpy as np
import os
import time
import pickle
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

path = "./db/api_info/"
# Load from the JSON file, not the CSV
with open(path + "api_information.json", 'r') as f:
    api_data = json.load(f)

passage_data = pd.DataFrame(api_data)

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = openai_api_key

embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")

start = time.time()
metadatas = []
# Ensure 'summary' column exists and handle potential missing summaries
if 'summary' not in passage_data.columns:
    # If no 'summary', use 'description' as a fallback. If neither, use a blank string.
    passage_data['summary'] = passage_data.get('description', pd.Series("", index=passage_data.index))

# Drop rows where summary is null to prevent errors
passage_data.dropna(subset=['summary'], inplace=True)

for index, row in passage_data.iterrows():
    doc_meta = {
        "id": row.get('Id'),
        "name": row.get('name'),
    }
    metadatas.append(doc_meta)

faiss = FAISS.from_texts(passage_data['summary'].tolist(), embedding_function, metadatas)
print("Time Taken --> ", time.time()-start) 

faiss.save_local(path + 'vectordb/LangChain_FAISS', "api_vec")