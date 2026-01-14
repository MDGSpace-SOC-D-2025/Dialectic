from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os

try:
    import chromadb
    print("chromadb imported")
    client = chromadb.PersistentClient(path="./test_chroma_db")
    print("PersistentClient created")
except Exception as e:
    print(f"Error creating client: {e}")

try:
    embeddings = OpenAIEmbeddings(api_key="test") # Dummy
    print("Attempting Chroma init with persist_directory...")
    Chroma(persist_directory="./test_chroma", embedding_function=embeddings)
    print("Success with persist_directory")
except Exception as e:
    print(f"Failed with persist_directory: {e}")

try:
    print("Attempting Chroma init with persistence_directory...")
    Chroma(persistence_directory="./test_chroma", embedding_function=embeddings)
    print("Success with persistence_directory")
except Exception as e:
    print(f"Failed with persistence_directory: {e}")

try:
    print("Attempting Chroma init with client...")
    Chroma(client=client, collection_name="test_col", embedding_function=embeddings)
    print("Success with client")
except Exception as e:
    print(f"Failed with client: {e}")
