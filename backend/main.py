

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
import pandas as pd
import google.generativeai as genai
import os
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Set up Gemini API key
genai.configure(api_key="AIzaSyBwzbuL30EsbczQb9rWyBFVGB9S2rKG5y4")

# Initialize FastAPI
app = FastAPI()

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="qa_collection")

# Load CSV Data
csv_file = "datafile.csv"
df = pd.read_csv(csv_file)

# Function to generate embeddings using Gemini
def generate_embedding(text):
    try:
        response = genai.embed_content(
            model="models/embedding-001",  # Correct Gemini embedding model
            content=text,
            task_type="retrieval_document"
        )
        return response["embedding"]  # Extract the embedding vector
    except Exception as e:
        print("Error generating embedding:", str(e))
        return None

# Check if embeddings are already stored
if collection.count() == 0:
    print("Generating and storing embeddings in ChromaDB...")
    for index, row in df.iterrows():
        question = row["question"]
        answer = row["answer"]
        
        embedding = generate_embedding(question)
        
        if embedding:  # Only add if embedding is generated
            collection.add(
                ids=[str(index)], 
                embeddings=[embedding], 
                metadatas=[{"question": question, "answer": answer}]
            )
    print("Embeddings stored successfully!")
else:
    print(f"Embeddings already exist. Collection count: {collection.count()}")

# Define request model
class QueryRequest(BaseModel):
    query: str

# Function to retrieve the most relevant answer
def get_best_answer(query):
    query_embedding = generate_embedding(query)

    if query_embedding is None:
        return "Sorry, I couldn't generate an embedding for your query."

    print("Query Embedding:", query_embedding)  # Debugging

    results = collection.query(query_embeddings=[query_embedding], n_results=1)

    print("ChromaDB Response:", results)  # Debugging

    if results["distances"][0][0] > 0.3:
        return "Sorry, I couldn't find a relevant answer."

    if results["metadatas"] and results["metadatas"][0]:
        best_match = results["metadatas"][0][0]  # Top result
        return best_match["answer"]

    return "Sorry, I couldn't find a relevant answer."



# Function to refine the response using Gemini
def refine_with_gemini(context):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Refine and simplify this response: {context}")
    return response.text if response.text else context

# FastAPI Route: Chatbot Endpoint
@app.post("/chat")
def chat(request: QueryRequest):
    try:
        query = request.query
        best_answer = get_best_answer(query)
        refined_answer = refine_with_gemini(best_answer)
        return {"response": refined_answer}
    except Exception as e:
        print("Error in /chat route:", str(e))  # Debugging
        raise HTTPException(status_code=500, detail=str(e))
