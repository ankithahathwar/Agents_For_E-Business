# pyrefly: ignore [missing-import]
import os
import json
import psycopg2
# pyrefly: ignore [untyped-import]
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from groq import Groq

# 1. Initialize environment properties and credentials
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="Agents_For_E-Business Intelligent Core")

# Enable CORS so your future frontend website can securely talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our twin cloud AI drivers
gemini_client = genai.Client()
# pyrefly: ignore [untyped-import]
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define what an incoming message structure looks like using Pydantic
class ChatRequest(BaseModel):
    user_message: str

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_gemini_embedding(text: str):
    """Translates text data into a 3072-dimension coordinate vector."""
    response = gemini_client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )
    # pyrefly: ignore [unsupported-operation]
    return response.embeddings[0].values

# =====================================================================
# THE MASTER AI CHAT CONCIERGE ENDPOINT
# =====================================================================
@app.post("/api/chat")
def handle_concierge_chat(payload: ChatRequest):
    try:
        user_input = payload.user_message
        
        # STEP 1: Convert user text to vector coordinates
        query_vector = get_gemini_embedding(user_input)
        
        # STEP 2: Query PostgreSQL vector table to find the best relevant match
        conn = get_db_connection()
        cursor = conn.cursor()
        
        search_query = """
        SELECT p.name, p.category, p.description, p.customization_matrix
        FROM catalog_embeddings c
        JOIN products p ON c.base_product_id = p.base_product_id
        ORDER BY c.embedding <=> %s::vector
        LIMIT 1;
        """
        cursor.execute(search_query, (query_vector,))
        db_match = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not db_match:
            raise HTTPException(status_code=404, detail="No inventory products found.")
            
        # STEP 3: Bundle user input + our raw database row matrix into a secret prompt package
        system_instruction = (
            "You are an expert luxury bespoke fashion concierge for 'Agents_For_E-Business'. "
            "Your job is to assist confused users by offering them clear, structured options based "
            "strictly on the product data provided. Do not invent options that are not explicitly listed.\n\n"
            f"Here is the valid product inventory item matching their vibe:\n"
            # pyrefly: ignore [bad-index]
            f"Product Name: {db_match['name']}\n"
            # pyrefly: ignore [bad-index]
            f"Category: {db_match['category']}\n"
            # pyrefly: ignore [bad-index]
            f"Description: {db_match['description']}\n"
            # pyrefly: ignore [bad-index]
            f"Full Customization Options Matrix: {json.dumps(db_match['customization_matrix'])}\n\n"
            "INSTRUCTIONS:\n"
            "1. Be conversational, elegant, and helpful.\n"
            "2. Always offer possible options from the matrix (fabrics, styling, colors) to guide them.\n"
            "3. Provide explicit website links for options using standard markdown syntax. "
            "Use the format [Text Here](/shop/suits/sartorial-bespoke) or similar based on item types.\n"
        )
        
        # STEP 4: Fire the secret package outbound to Groq's endpoint for high-speed sentence creation
        groq_response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_input}
            ],
            temperature=0.6
        )
        
        ai_reply = groq_response.choices[0].message.content
        
        # STEP 5: Return only the clean, conversational response to the client chat bubble
        return {"reply": ai_reply}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat orchestration failure: {str(e)}")