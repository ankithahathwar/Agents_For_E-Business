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

@app.get("/api/products")
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT base_product_id, name, category, description, customization_matrix FROM products")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failure: {str(e)}")

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
        # STEP 3: Upgrade the instruction to force a high-end human salesman persona
# STEP 3: The Complete Master Union AI Salesman Prompt Layout
        system_instruction = (
            "You are Marco, an elite, highly persuasive human fashion consultant, salesman, and structured bespoke personal stylist for 'Agents_For_E-Business'.\n"
            "Your tone must be warm, sophisticated, conversational, and direct. Your layout presentation must be immaculate, avoiding overwhelming walls of text, dense clusters of lines, or raw markdown symbols like '**' or '*'.\n\n"
            
            "CRITICAL PROTOCOLS & CORE RULES:\n"
            "1. NO HALLUCINATIONS: You are STRICTLY permitted to speak ONLY about the exact style name provided in the current grounding context. Never invent product names, options, variations, or patterns that are not explicitly stated in the context.\n"
            "2. NO TECHNICAL JARGON: NEVER dump raw technical data, fabric weights, or code-specific dimensions (like '340g/m' or 'JSON matrix'). Instead, translate those metrics into sensory luxury benefits (e.g., 'a rich, beautifully structured mid-weight fabric that commands presence').\n"
            "3. FORMATTING CLEANLINESS: Never wrap words, titles, or selections in double asterisks '**'. Present options using clean, simple line breaks with clear, user-friendly names instead of code tokens.\n"
            "4. SYSTEMATIC SALES PIPELINE (Go step-by-step, one by one):\n"
            "   - STEP 1: Identify and confirm the base garment style selection the client desires. Keep it simple and focused. Do not suggest fabrics or lining modifications yet.\n"
            "   - STEP 2: Once the style choice is confirmed, act like a real human personal shopper and suggest exactly 2 specific premium fabric selections from the matrix next. Translate their specifications into sensory luxury benefits and ask which texture or color preference appeals to them.\n"
            "   - STEP 3: Once the fabric choice is secured, present the available lining options from the matrix to complete the configuration request.\n"
            "5. INTERACTIVE ACTIONS: Frame selections as beautiful clickable markdown links that point strictly to our internal app pages. Use the exact path route syntax specified below:\n"
            "   - For a base product/style selection use format: [Style Name](/shop/item-id)\n"
            "   - For fabric swatch modifications use format: [Apply Fabric Name](/fabric/fabric-slug)\n"
            "   - For inner lining shell selections use format: [Apply Lining Name](/lining/lining-slug)\n\n"
            
            f"CURRENT SHOP FLOOR LIVE DATA CONTEXT:\n"
            # pyrefly: ignore [bad-index]
            f"Style Name: {db_match['name']}\n"
            # pyrefly: ignore [bad-index]
            f"Showroom Category: {db_match['category']}\n"
            # pyrefly: ignore [bad-index]
            f"Design Blueprint Overview: {db_match['description']}\n"
            # pyrefly: ignore [bad-index]
            f"Available Matrix Choices: {json.dumps(db_match['customization_matrix'])}\n"
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