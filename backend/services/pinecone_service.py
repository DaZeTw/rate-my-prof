import os
from pinecone import Pinecone
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

api_key = os.getenv('PINECONE_API_KEY')
environment = os.getenv('PINECONE_ENVIRONMENT')
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize Pinecone
pc = Pinecone(api_key=api_key)
index = pc.Index("test")  # Ensure this index is created with dimension 1536

# Set up OpenAI API key
openai.api_key = openai_api_key

def generate_embedding(text):
    # Generate embedding using OpenAI's text-embedding-ada-002 model
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    embedding = response['data'][0]['embedding']
    return embedding  # This should return a 1536-dimensional vector

def store_review(unique_id, professor_name, department, school, overall_quality, would_take_again, level_of_difficulty, review_text):
    embedding = generate_embedding(review_text)
    vector = {
        'id': unique_id,  # Use the unique ID as the vector's ID
        'values': embedding,
        'metadata': {
            'professor_name': professor_name,
            'department': department,
            'school': school,
            'overall_quality': overall_quality,
            'would_take_again': would_take_again,
            'level_of_difficulty': level_of_difficulty,
            'review': review_text
        }
    }
    index.upsert(vectors=[vector])

def query_review(query_text):
    embedding = generate_embedding(query_text)
    # Include metadata in the query
    response = index.query(vector=embedding, top_k=3, include_metadata=True)
    return response['matches']
