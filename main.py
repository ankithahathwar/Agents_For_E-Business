# pyrefly: ignore [missing-import]
import os
import json
# pyrefly: ignore [untyped-import]
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

# --- STATE CONTEXT MEMORY VAULT ---
# This temporary dictionary stores histories like: {"session_abc": [{"role": "user", "content": "..."}, ...]}
SESSION_MEMORY = {}

# Expand our incoming tracking layout to expect a session identification tag
class ChatRequest(BaseModel):
    user_message: str
    session_id: str = "default_shopper" # Fallback tracking session default tag

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_gemini_embedding(text: str):
    response = gemini_client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )
    # pyrefly: ignore [unsupported-operation]
    return response.embeddings[0].values

@app.post("/api/chat")
def handle_concierge_chat(payload: ChatRequest):
    try:
        user_input = payload.user_message
        session_key = payload.session_id
        
        # 1. If this is a brand new user session, open up a fresh history log book for them
        if session_key not in SESSION_MEMORY:
            SESSION_MEMORY[session_key] = []
            
        # 2. Convert user text to vector coordinates
        query_vector = get_gemini_embedding(user_input)
        
        # 3. Query PostgreSQL vector table to find the best relevant match
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
            
        # 4. Construct our underlying data grounding instruction
        system_instruction = (
            "You are an expert luxury bespoke fashion concierge for 'Agents_For_E-Business'. "
            "Your job is to assist confused users by offering them clear, structured options based "
            "strictly on the product data provided. Do not invent options that are not explicitly listed.\n\n"
            f"Here is the verified catalog item relevant to their current exploration context:\n"
            # pyrefly: ignore [bad-index]
            f"Product Name: {db_match['name']}\n"
            # pyrefly: ignore [bad-index]
            f"Category: {db_match['category']}\n"
            # pyrefly: ignore [bad-index]
            f"Description: {db_match['description']}\n"
            # pyrefly: ignore [bad-index]
            f"Full Customization Options Matrix: {json.dumps(db_match['customization_matrix'])}\n\n"
            "INSTRUCTIONS:\n"
            "1. Review the message history array provided to maintain continuity.\n"
            "2. Be elegantly conversational, conversational, and direct.\n"
            "3. Guide them sequentially from choosing a fabric to picking accents.\n"
        )
        
        # 5. Build our sliding conversation payload history package for Groq
        # We start with our core master layout parameters
        groq_messages = [{"role": "system", "content": system_instruction}]
        
        # We append all their previous historical back-and-forth interactions secretly
        for past_message in SESSION_MEMORY[session_key]:
            groq_messages.append(past_message)
            
        # Finally, append the current incoming statement
        groq_messages.append({"role": "user", "content": user_input})
        
        # 6. Fire the comprehensive memory sequence outbound to Groq
        # pyrefly: ignore [no-matching-overload]
        groq_response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            temperature=0.5
        )
        
        ai_reply = groq_response.choices[0].message.content
        
        # 7. COMMIT CURRENT EXCHANGE PERMANENTLY TO SERVER MEMORY LOG
        SESSION_MEMORY[session_key].append({"role": "user", "content": user_input})
        SESSION_MEMORY[session_key].append({"role": "assistant", "content": ai_reply})
        
        # Truncate conversation window limits if memory grows past 10 turns to protect context buffers
        if len(SESSION_MEMORY[session_key]) > 20:
            SESSION_MEMORY[session_key] = SESSION_MEMORY[session_key][-20:]
            
        return {"reply": ai_reply}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat orchestration failure: {str(e)}")