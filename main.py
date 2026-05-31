# pyrefly: ignore [missing-import]
import os
# pyrefly: ignore [untyped-import]
import psycopg2
# pyrefly: ignore [untyped-import]
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Query
from dotenv import load_dotenv
from google import genai

# 1. Load cloud database URLs and AI API keys
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Initialize the backend engine and Gemini client
app = FastAPI(title="Agents_For_E-Business Core Backend")
client = genai.Client()

def get_db_connection():
    # pyrefly: ignore [untyped-import]
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_query_vector(text_to_search: str):
    """Translates incoming text criteria into a matching 3072-dimension coordinate frame."""
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text_to_search
    )
    # pyrefly: ignore [unsupported-operation]
    return response.embeddings[0].values

@app.get("/")
def read_root():
    return {"status": "online", "message": "The Agents_For_E-Business backend engine is humming."}

@app.get("/api/products")
def get_all_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT base_product_id, name, category, description FROM products;")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# Endpoint 4: The Core AI Recommendation Router Engine
@app.get("/api/recommend")
def recommend_products_by_vibe(vibe: str = Query(..., description="The user's descriptive style preference or situation")):
    try:
        # Convert the user's incoming search string parameters into a live vector
        query_vector = get_query_vector(vibe)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute the pgvector cosine distance operation against our vector table
        # We also JOIN back to our main products table to pull the relational data details simultaneously!
        search_query = """
        SELECT 
            p.base_product_id, 
            p.name, 
            p.category, 
            p.description,
            (1 - (c.embedding <=> %s::vector)) AS ai_match_accuracy
        FROM catalog_embeddings c
        JOIN products p ON c.base_product_id = p.base_product_id
        ORDER BY c.embedding <=> %s::vector
        LIMIT 2;
        """
        
        cursor.execute(search_query, (query_vector, query_vector))
        recommendations = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "search_intent_analyzed": vibe,
            "top_matches": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Recommendation Engine error: {str(e)}")