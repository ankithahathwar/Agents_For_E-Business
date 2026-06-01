# pyrefly: ignore [missing-import]
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from groq import Groq

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

gemini_client = genai.Client()
# pyrefly: ignore [untyped-import]
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- STATE CONTEXT MEMORY VAULT ---
# Tracks message histories and persistent session category locks inside server RAM
SESSION_MEMORY = {}

class ChatRequest(BaseModel):
    user_message: str
    session_id: str = "default_shopper"

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
        
        # Initialize storage architecture if it is a fresh session key
        if session_key not in SESSION_MEMORY:
            SESSION_MEMORY[session_key] = {
                "messages": [],
                "active_category": None
            }
            
        user_msg_lower = user_input.lower()
        
        # 1. CATEGORY LOCK MATRIX: Catch explicit intent to browse a new department
        category_keywords = {
            "suits - men": "Suits - Men", "men suit": "Suits - Men", "mens suit": "Suits - Men",
            "suits - women": "Suits - Women", "women suit": "Suits - Women", "womens suit": "Suits - Women",
            "gown": "Gowns",
            "saree": "Sarees",
            "coats - men": "Coats - Men", "men coat": "Coats - Men",
            "coats - women": "Coats - Women", "women coat": "Coats - Women",
            "scarfs - men": "Scarfs - Men", "men scarf": "Scarfs - Men",
            "scarfs - women": "Scarfs - Women", "women scarf": "Scarfs - Women"
        }
        
        explicit_switch = False
        for keyword, category_name in category_keywords.items():
            if keyword in user_msg_lower:
                SESSION_MEMORY[session_key]["active_category"] = category_name
                explicit_switch = True
                break
                
        # 2. Convert active intent text into vector coordinates
        query_vector = get_gemini_embedding(user_input)
        
        # 3. DATABASE SEARCH ENGINE: Enforce context-locking retrieval loops
        conn = get_db_connection()
        cursor = conn.cursor()
        
        current_locked_cat = SESSION_MEMORY[session_key]["active_category"]
        
        if current_locked_cat and not explicit_switch:
            # STICKY CATEGORY FILTER: Pull alternative choices only from the active locked department
            search_query = """
            SELECT p.base_product_id, p.name, p.category, p.description, p.customization_matrix
            FROM catalog_embeddings c
            JOIN products p ON c.base_product_id = p.base_product_id
            WHERE p.category = %s
            ORDER BY c.embedding <=> %s::vector
            LIMIT 4;
            """
            cursor.execute(search_query, (current_locked_cat, query_vector))
        else:
            # FLOOR SEARCH: Search across all 160 varieties if category is neutral or switching
            search_query = """
            SELECT p.base_product_id, p.name, p.category, p.description, p.customization_matrix
            FROM catalog_embeddings c
            JOIN products p ON c.base_product_id = p.base_product_id
            ORDER BY c.embedding <=> %s::vector
            LIMIT 4;
            """
            cursor.execute(search_query, (query_vector,))
            
        db_matches = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not db_matches:
            raise HTTPException(status_code=404, detail="No matching apparel records found.")
            
        # Fallback category tag initialization
        if not SESSION_MEMORY[session_key]["active_category"]:
            SESSION_MEMORY[session_key]["active_category"] = db_matches[0]["category"]
            
        # 4. Extract options and construct the context grounding block text
        inventory_context_string = ""
        for index, item in enumerate(db_matches, 1):
            inventory_context_string += (
                f"ITEM {index}:\n"
                f"ID: {item['base_product_id']}\n"
                f"Name: {item['name']}\n"
                f"Category: {item['category']}\n"
                f"Description: {item['description']}\n"
                f"Matrix: {json.dumps(item['customization_matrix'])}\n"
                f"----------------------------------------\n"
            )

        # 5. THE COMPLETE MASTER UNION AI SALESMAN PROMPT CONFIGURATION
        system_instruction = (
            "You are Marco, an elite, highly persuasive human fashion consultant, salesman, and structured bespoke stylist for 'Agents_For_E-Business'.\n"
            "Your tone must be warm, sophisticated, conversational, and direct. Your layout presentation must be immaculate, avoiding overwhelming walls of text, dense clusters of lines, or raw markdown operators like '**' or '*'.\n\n"
            
            "CRITICAL PROTOCOLS & CORE RULES:\n"
            "1. NO HALLUCINATIONS: You are STRICTLY permitted to speak ONLY about the exact product items provided in the current live data context below. Never invent product names, options, variations, or patterns that are not explicitly stated in the context.\n"
            "2. NO TECHNICAL JARGON: NEVER dump raw technical data, fabric weights, or code-specific variables (like '340g/m' or 'JSON matrix'). Instead, translate those metrics into sensory luxury benefits (e.g., 'a rich, beautifully structured mid-weight fabric that commands presence').\n"
            "3. FORMATTING CLEANLINESS: Never wrap words, titles, options, or selections in double asterisks '**'. Present items using clean, simple line breaks with clear, user-friendly names instead of code tokens.\n"
            "4. HANDLING GENERIC/BROAD REQUESTS: If the user makes a broad request (e.g., 'show me some gowns', 'what other options are there', 'suits for men'), DO NOT jump straight to a single option or fabric selection. "
            "Instead, introduce 3 distinct varieties from the context below using clean line breaks, offering a concise, alluring sensory sentence for each, and present them as clickable text links using the format: [Style Name](/shop/id).\n"
            "5. THE SYSTEMATIC SALES DESIGN PIPELINE: Once the customer has expressed a clear preference or selected a specific silhouette from your choices, lock into that style and proceed with the step-by-step funnel sequence:\n"
            "   - STEP 1: Acknowledge their selection elegantly and summarize the aesthetic value of that specific cut layout. Keep it focused. Do not suggest fabrics or linings yet.\n"
            "   - STEP 2: Once the style choice is confirmed, act like a real human personal shopper and suggest exactly 2 compatible fabric options available inside that specific item's matrix data. Translate their specifications into sensory luxury benefits and ask which texture or color preference appeals to them. Present them as links: [Apply Fabric Name](/fabric/name-slug).\n"
            "   - STEP 3: Once the fabric choice is secured, present the available inner lining options from the matrix to complete the configuration request. Present them as links: [Apply Lining Description](/lining/slug).\n"
            "6. INTERACTIVE ACTIONS: Frame options as clean clickable markdown text links that point strictly to our internal app paths using the formats mapped out in the rules above.\n\n"
            
            f"CURRENT LIVE DATA WINDOW (TOP TRACKED INVENTORY MATCHES):\n"
            f"{inventory_context_string}"
        )
        
        # 6. Assemble complete conversation array and execute network call to Groq
        groq_messages = [{"role": "system", "content": system_instruction}]
        for past_message in SESSION_MEMORY[session_key]["messages"]:
            groq_messages.append(past_message)
        groq_messages.append({"role": "user", "content": user_input})
        
        groq_response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            temperature=0.3
        )
        
        ai_reply = groq_response.choices[0].message.content
        
        # Commit dialog records to cache logs
        SESSION_MEMORY[session_key]["messages"].append({"role": "user", "content": user_input})
        SESSION_MEMORY[session_key]["messages"].append({"role": "assistant", "content": ai_reply})
        
        if len(SESSION_MEMORY[session_key]["messages"]) > 20:
            SESSION_MEMORY[session_key]["messages"] = SESSION_MEMORY[session_key]["messages"][-20:]
            
        return {"reply": ai_reply}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Concierge runtime interruption: {str(e)}")