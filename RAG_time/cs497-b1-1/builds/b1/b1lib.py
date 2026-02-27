import os
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv('sample.env')

embed = OllamaEmbeddings(model="mxbai-embed-large")

vector_store = Chroma(collection_name='cs497_b1',
                      embedding_function=embed,
                      persist_directory='chroma_db')
# not sure why this isn't getting triggered from my lab1lib
def rag(query, k=3):
    query_embed = embed.embed_query(query)
    docs = vector_store.similarity_search_by_vector(embedding=query_embed, k=k)
    print(f"DEBUG: Found {len(docs)} documents for query") # added for debugging purposes
    return docs