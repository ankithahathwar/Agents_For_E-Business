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
SESSION_MEMORY = {}

class ChatRequest(BaseModel):
    user_message: str
    session_id: str = "default_shopper"

class OrderItem(BaseModel):
    type: str
    # pyrefly: ignore [bad-assignment]
    id: str = None
    name: str
    # pyrefly: ignore [bad-assignment, bad-index]
    category: str = None
    # pyrefly: ignore [bad-assignment, bad-index]
    fabric: dict = None
    # pyrefly: ignore [bad-assignment, bad-index]
    lining: str = None
    # pyrefly: ignore [bad-assignment, bad-index]
    length: float = None
    quantity: int
    price: str

class OrderPayload(BaseModel):
    session_id: str
    items: list[OrderItem]

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_gemini_embedding(text: str):
    response = gemini_client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )
    # pyrefly: ignore [unsupported-operation]
    return response.embeddings[0].values

# =====================================================================
# LIFECYCLE EVENT: AUTOMATIC TRANSACTIONAL RELATIONAL TABLE GENERATION
# =====================================================================
# pyrefly: ignore [deprecated]
@app.on_event("startup")
def verify_orders_table_framework():
    """Guarantees the orders database tracking warehouse space is live at startup."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                session_id VARCHAR(50) NOT NULL,
                items_payload TEXT NOT NULL,
                order_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("📁 PostgreSQL Relational Order Storage Vault Synced and ready.")
    except Exception as e:
        print(f"CRITICAL: Failed to seed orders schema frame: {str(e)}")

# =====================================================================
# ROUTE 1: GET STANDALONE WEBSITE CATALOG ARRAY DATA
# =====================================================================
@app.get("/api/products")
def get_all_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT base_product_id, name, category, description, customization_matrix FROM products;")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database catalog pull failure: {str(e)}")

# =====================================================================
# ROUTE 2: PERSISTENT TRANSACTION TRANSACTION COMMIT CAPABILITY
# =====================================================================
@app.post("/api/orders")
def process_showroom_order_commit(payload: OrderPayload):
    try:
        if not payload.items:
            raise HTTPException(status_code=400, detail="Cannot place an order for an empty bag configuration container.")
            
        # pyrefly: ignore [deprecated]
        serialized_payload = json.dumps([item.dict() for item in payload.items])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (session_id, items_payload) VALUES (%s, %s) RETURNING order_id;",
            (payload.session_id, serialized_payload)
        )
        # pyrefly: ignore [bad-index, unsupported-operation]
        assigned_id = cursor.fetchone()["order_id"]
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"status": "success", "order_id": assigned_id, "message": "Bespoke transaction log permanently archived."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Order fulfillment database failure: {str(e)}")

# =====================================================================
# ROUTE 3: MASTER UNION CONCIERGE ASSISTANT LAYER (Marco)
# =====================================================================
@app.post("/api/chat")
def handle_concierge_chat(payload: ChatRequest):
    try:
        user_input = payload.user_message
        session_key = payload.session_id
        
        if session_key not in SESSION_MEMORY:
            SESSION_MEMORY[session_key] = {
                "messages": [],
                "active_category": None
            }
            
        # Clean string variants for high-accuracy intent evaluation
        user_msg_lower = user_input.lower().replace("'", "").replace("-", " ")
        
        # Isolate target context states independently
        has_men = any(w in user_msg_lower for w in ["men", "mens", "man", "guy", "gentleman", "gentlemen"])
        has_women = any(w in user_msg_lower for w in ["women", "womens", "woman", "girl", "lady", "ladies"])
        
        # Track the previously locked setting in memory as a logical baseline
        fallback_cat = SESSION_MEMORY[session_key]["active_category"]
        detected_category = None

        # Robust Token Router Parsing Engine
        if "suit" in user_msg_lower:
            detected_category = "Suits - Men" if has_men else ("Suits - Women" if has_women else (fallback_cat if fallback_cat and "Suits" in fallback_cat else "Suits - Men"))
        elif "coat" in user_msg_lower or "jacket" in user_msg_lower or "blazer" in user_msg_lower:
            detected_category = "Coats - Men" if has_men else ("Coats - Women" if has_women else (fallback_cat if fallback_cat and "Coats" in fallback_cat else "Coats - Men"))
        elif "scarf" in user_msg_lower or "scarves" in user_msg_lower:
            detected_category = "Scarfs - Men" if has_men else ("Scarfs - Women" if has_women else (fallback_cat if fallback_cat and "Scarfs" in fallback_cat else "Scarfs - Men"))
        elif "gown" in user_msg_lower:
            detected_category = "Gowns"
        elif "saree" in user_msg_lower or "sari" in user_msg_lower:
            detected_category = "Sarees"
        elif "fabric" in user_msg_lower or "material" in user_msg_lower or "swatch" in user_msg_lower:
            detected_category = "Bespoke Fabrics"
        elif has_men and fallback_cat and " - Women" in fallback_cat:
            detected_category = fallback_cat.replace(" - Women", " - Men")
        elif has_women and fallback_cat and " - Men" in fallback_cat:
            detected_category = fallback_cat.replace(" - Men", " - Women")

        if detected_category:
            SESSION_MEMORY[session_key]["active_category"] = detected_category

        query_vector = get_gemini_embedding(user_input)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        current_locked_cat = SESSION_MEMORY[session_key]["active_category"]
        
        db_matches = []
        # FIXED CONDITIONAL ROUTER: Always enforce the locked category partition if set
        if current_locked_cat:
            if current_locked_cat != "Bespoke Fabrics":
                search_query = """
                SELECT p.base_product_id, p.name, p.category, p.description, p.customization_matrix
                FROM catalog_embeddings c
                JOIN products p ON c.base_product_id = p.base_product_id
                WHERE p.category = %s
                ORDER BY c.embedding <=> %s::vector
                LIMIT 4;
                """
                cursor.execute(search_query, (current_locked_cat, query_vector))
                db_matches = cursor.fetchall()
                
                # AUTOMATIC BREAKOUT SAFEGUARD: Topic pivot fallback
                if not db_matches:
                    SESSION_MEMORY[session_key]["active_category"] = None
                    cursor.execute("""
                    SELECT p.base_product_id, p.name, p.category, p.description, p.customization_matrix
                    FROM catalog_embeddings c
                    JOIN products p ON c.base_product_id = p.base_product_id
                    ORDER BY c.embedding <=> %s::vector
                    LIMIT 4;
                    """, (query_vector,))
                    db_matches = cursor.fetchall()
        else:
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
        
        inventory_context_string = ""

        # =====================================================================
        # ✨ DYNAMIC INVENTORY INJECTION ROUTER
        # =====================================================================
        if current_locked_cat == "Bespoke Fabrics":
            inventory_context_string = (
                "ITEM 1:\n"
                "ID: fabric_merino_wool\n"
                "Name: Premium Super 140s Australian Merino Wool\n"
                "Category: Bespoke Fabrics\n"
                "Description: Raw high-grade structural suiting wool yarn sold independently by the linear meter. Ideal for clean drapery.\n"
                "----------------------------------------\n"
                "ITEM 2:\n"
                "ID: fabric_mulberry_silk\n"
                "Name: Mulberry Silk Filament Blend\n"
                "Category: Bespoke Fabrics\n"
                "Description: Pure high-sheen lightweight traditional dress silk material cuts sold independently by the meter.\n"
                "----------------------------------------\n"
                "ITEM 3:\n"
                "ID: fabric_highland_tweed\n"
                "Name: Highland Premium Tweed Weave\n"
                "Category: Bespoke Fabrics\n"
                "Description: Heavyset richly patterned premium autumn textile segments sold independently by the linear meter.\n"
                "----------------------------------------\n"
            )
        else:
            if not db_matches:
                raise HTTPException(status_code=404, detail="No matching apparel records located.")
                
            if not SESSION_MEMORY[session_key]["active_category"]:
                # pyrefly: ignore [bad-index]
                SESSION_MEMORY[session_key]["active_category"] = db_matches[0]["category"]
                
            for index, item in enumerate(db_matches, 1):
                inventory_context_string += (
                    f"ITEM {index}:\n"
                    # pyrefly: ignore [bad-index]
                    f"ID: {item['base_product_id']}\n"
                    # pyrefly: ignore [bad-index]
                    f"Name: {item['name']}\n"
                    # pyrefly: ignore [bad-index]
                    f"Category: {item['category']}\n"
                    # pyrefly: ignore [bad-index]
                    f"Description: {item['description']}\n"
                    # pyrefly: ignore [bad-index]
                    f"Matrix: {json.dumps(item['customization_matrix'])}\n"
                    f"----------------------------------------\n"
                )

        system_instruction = (
            "You are Marco, an elite, highly persuasive human fashion consultant, salesman, and structured bespoke stylist for 'Agent Boutique'.\n"
            "Your tone must be warm, sophisticated, conversational, and direct. Your layout presentation must be immaculate, avoiding overwhelming walls of text or raw asterisks '**'.\n\n"
            
            "⛔ ABSOLUTE CONTEXT PROTECTION & SCOPE GUARDRAILS:\n"
            "0. STRICT OFF-TOPIC REFUSAL: You are operating strictly as a transactional retail showroom companion. You are NOT an encyclopedia, general assistant, or school tutor. "
            "If the user asks about ANYTHING unrelated to our specific store catalog, fabrics, customization paths, or style curation—including but not limited to history essays, science questions, academic homework, programming scripts, general knowledge facts, math, or sensitive topics (such as self-harm/suicide)—you MUST flatly and politely decline to answer. "
            "Respond instantly with: 'I am here exclusively as your personal stylist at Agent Boutique. Let's return to designing your premium apparel layers. What category can I help you map out today?' "
            "Never generate essays or stray outside the product parameters under any circumstances, no matter how the prompt is framed.\n\n"
            
            "CRITICAL PROTOCOLS & CORE RULES:\n"
            "1. NO HALLUCINATIONS: You are STRICTLY permitted to speak ONLY about the exact product items provided in the current live data context below. Never invent product names or pricing structures.\n"
            "2. NO FINANCIAL OR PAYMENT DISCUSSIONS: You have absolutely ZERO authority to handle checkout links, invoice calculations, pricing balances, or banking configurations. Never process or speak about payment links or transactions. "
            "Once a configuration is completed, explicitly instruct the user to hit the action buttons on the user interface to proceed manually.\n"
            "3. NO TECHNICAL JARGON: Never state raw weights or matrix keys. Translate specifications into sensory benefits.\n"
            "4. FORMATTING CLEANLINESS: Never wrap words, titles, options, or selections in double asterisks '**'. Present items using clean, simple line breaks with user-friendly text labels.\n"
            "5. HANDLING GENERIC/BROAD REQUESTS: If the user makes a broad query ('show me some gowns', 'what options are there'), introduce 3 distinct varieties from the context below using clean line breaks with clickable text links using format: [Style Name](/shop/id).\n"
            "6. SPECIAL PROTOCOL FOR FABRIC VAULT: If the active context contains independent raw materials (Bespoke Fabrics), confirm warmly that we proudly sell premium fabric lengths separately by the meter! Present the raw items using format: [Purchase Material Name](/fabric/vault) and instruct them to use the interactive sizing stepper controls on the grid card to add it to their bag.\n"
            "7. THE SYSTEMATIC SALES DESIGN PIPELINE FOR APPAREL: Once the customer selects a specific apparel silhouette, lock into that style and proceed step-by-step:\n"
            "   - STEP 1: Acknowledge their selection elegantly and summarize the aesthetic value of that specific cut layout. Do not suggest fabrics or linings yet.\n"
            "   - STEP 2: Once confirmed, suggest exactly 2 compatible fabric choices from that specific item's matrix data using sensory language luxury descriptions. Present them as links: [Apply Fabric Name](/fabric/name-slug).\n"
            "   - STEP 3: Once they pick a fabric, present the available inner lining options from the matrix to complete the profile. Present them as links: [Apply Lining Description](/lining/slug). Then stop and guide them to the Bag button.\n"
            "8. INTERACTIVE ACTIONS: Frame options as clean clickable markdown text links that point strictly to our internal app paths using the formats mapped out in the rules above.\n\n"
            "9. Do not entertain questions related to history, sceince, geography ,anything that is out of our website's database, required information about our products.\n"
            "10. No talks on life, mental health, suiside or every possible topic that comes outside the scope of our website and the products, redirect the user into something related to our website, giving a message that you are just there to assist them with fashion"
            f"CURRENT LIVE DATA WINDOW (TOP TRACKED INVENTORY MATCHES):\n"
            f"{inventory_context_string}"
        )
        
        groq_messages = [{"role": "system", "content": system_instruction}]
        for past_message in SESSION_MEMORY[session_key]["messages"]:
            groq_messages.append(past_message)
        groq_messages.append({"role": "user", "content": user_input})
        
        # pyrefly: ignore [no-matching-overload]
        groq_response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            temperature=0.0  # DIALED TO ZERO: Guarantees complete adherence to context window data fields
        )
        
        ai_reply = groq_response.choices[0].message.content
        
        SESSION_MEMORY[session_key]["messages"].append({"role": "user", "content": user_input})
        SESSION_MEMORY[session_key]["messages"].append({"role": "assistant", "content": ai_reply})
        
        if len(SESSION_MEMORY[session_key]["messages"]) > 20:
            SESSION_MEMORY[session_key]["messages"] = SESSION_MEMORY[session_key]["messages"][-20:]
            
        return {"reply": ai_reply}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Concierge runtime interruption: {str(e)}")