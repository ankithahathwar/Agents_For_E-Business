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
# =====================================================================
# ROUTE 3: MASTER UNION CONCIERGE ASSISTANT LAYER (Marco)
# =====================================================================
# =====================================================================
# ROUTE 3: MASTER UNION CONCIERGE ASSISTANT LAYER (Marco) - HARDENED
# =====================================================================
def classify_user_intent(user_message: str) -> str:
    """Evaluates whether the incoming text belongs in our retail store or is completely off-topic."""
    router_instruction = (
        "You are the absolute front-door traffic router for 'Agent Boutique'. "
        "Your sole task is to classify the user's input message into one of two strict categories:\n"
        "1. SHOPPING - If the user is greeting you, asking about clothes, suits, fabrics, linings, ordering items, or requesting fashion curation.\n"
        "2. OFF_TOPIC - If the user is asking about general knowledge, music, celebrities, history, science, math, school homework, coding scripts, or any topic outside a clothing store catalog.\n\n"
        "CRITICAL: You must output EXACTLY one word: either 'SHOPPING' or 'OFF_TOPIC'. Do not include periods, spaces, prefaces, or explanations."
    )
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": router_instruction},
                {"role": "user", "content": user_message}
            ],
            temperature=0.0,
            max_tokens=5 # Hard ceiling so it can't blabber
        )
        # pyrefly: ignore [missing-attribute]
        return response.choices[0].message.content.strip().upper()
    except Exception:
        # Safe fallback: if the router fails, assume shopping to let the conversation try to continue
        return "SHOPPING"


@app.post("/api/chat")
def handle_concierge_chat(payload: ChatRequest):
    user_input = payload.user_message
    
    # 🛑 1. FIREWALL GATEKEEPER CHECK
    intent = classify_user_intent(user_input)
    if "OFF_TOPIC" in intent:
        return {
            "reply": "I am here exclusively as your personal stylist at Agent Boutique. Let's return to designing your premium apparel layers. What category can I help you map out today?"
        }
        
    session_key = payload.session_id
    
    # Initialize session memory safely
    if session_key not in SESSION_MEMORY:
        SESSION_MEMORY[session_key] = {
            "messages": [],
            "active_category": None,
            "last_context_string": ""
        }
    
    user_msg_lower = user_input.lower().replace("'", "").replace("-", " ")
    
    # 🎯 2. INTENT & GENDER EXTRACTION ENGINE
    has_both = "both" in user_msg_lower or ("men" in user_msg_lower and "women" in user_msg_lower)
    has_women = not has_both and any(w in user_msg_lower for w in ["women", "lady", "ladies", "woman"])
    has_men = not has_both and any(m in user_msg_lower for m in ["men", "man", "guy", "gents", "gentlem"])
    
    # Detect explicit product nouns
    mentioned_noun = None
    if "suit" in user_msg_lower: mentioned_noun = "Suits"
    elif any(c in user_msg_lower for c in ["coat", "jacket", "blazer"]): mentioned_noun = "Coats"
    elif any(s in user_msg_lower for s in ["scarf", "scarves"]): mentioned_noun = "Scarfs"
    elif "gown" in user_msg_lower: mentioned_noun = "Gowns"
    elif "saree" in user_msg_lower or "sari" in user_msg_lower: mentioned_noun = "Sarees"
    elif any(f in user_msg_lower for f in ["fabric", "material", "swatch"]): mentioned_noun = "Bespoke Fabrics"

    # 🔄 3. STATE MACHINE TRANSITION LOGIC
    fallback_cat = SESSION_MEMORY[session_key]["active_category"]
    detected_category = None
    inventory_context_string = ""
    is_ambiguous_turn = False

    # Check context history state
    has_cached_context = SESSION_MEMORY[session_key]["last_context_string"] != ""
    if has_cached_context:
        follow_up_tokens = ["3rd", "third", "1st", "first", "2nd", "second", "4th", "fourth", "one", "it", "this", "that", "about", "describe", "yes", "no"]
        is_conversational_follow_up = any(token in user_msg_lower for token in follow_up_tokens) and not mentioned_noun and not has_women and not has_men
    else:
        is_conversational_follow_up = False

    # 🔄 Route actions based on conversational state evaluation
    if is_conversational_follow_up:
        inventory_context_string = SESSION_MEMORY[session_key]["last_context_string"]
    else:
        # Evaluate state changes based on noun context
        if mentioned_noun:
            if mentioned_noun in ["Gowns", "Sarees", "Bespoke Fabrics"]:
                detected_category = mentioned_noun
            elif has_both:
                detected_category = None # Global multi-pull
            elif has_women:
                detected_category = f"{mentioned_noun} - Women"
            elif has_men:
                detected_category = f"{mentioned_noun} - Men"
            else:
                if fallback_cat and ("Men" in fallback_cat or "Women" in fallback_cat):
                    gender_suffix = "Men" if "Men" in fallback_cat else "Women"
                    detected_category = f"{mentioned_noun} - {gender_suffix}"
                else:
                    is_ambiguous_turn = True
        else:
            if fallback_cat:
                current_noun = fallback_cat.split(" - ")[0]
                if has_both:
                    detected_category = None
                elif has_women and current_noun in ["Suits", "Coats", "Scarfs"]:
                    detected_category = f"{current_noun} - Women"
                elif has_men and current_noun in ["Suits", "Coats", "Scarfs"]:
                    detected_category = f"{current_noun} - Men"
                else:
                    detected_category = fallback_cat
            else:
                is_ambiguous_turn = True

        # Commit structural updates to memory state slots
        if detected_category or has_both:
            SESSION_MEMORY[session_key]["active_category"] = detected_category

        # 🗄️ 4. SAFE-FAIL ZONE A: Database & Vector Extraction Layer
        if is_ambiguous_turn:
            inventory_context_string = (
                "CRITICAL ERROR CONTEXT: The customer requested apparel items but has not explicitly "
                "clarified whether they are looking for the Men's or Women's collection. Do NOT display or "
                "invent any inventory products yet. You must warmly and professionally ask the customer "
                "to clarify which gender collection they want to explore today before proceeding."
            )
            SESSION_MEMORY[session_key]["active_category"] = None
        else:
            try:
                query_vector = get_gemini_embedding(user_input)
                conn = get_db_connection()
                cursor = conn.cursor()
                current_locked_cat = SESSION_MEMORY[session_key]["active_category"]
                db_matches = []
                
                if current_locked_cat and current_locked_cat != "Bespoke Fabrics":
                    search_query = """
                    SELECT p.base_product_id, p.name, p.category, p.description, p.customization_matrix
                    FROM catalog_embeddings c
                    JOIN products p ON c.base_product_id = p.base_product_id
                    WHERE p.category = %s
                    ORDER BY c.embedding <=> %s::vector
                    LIMIT 10;
                    """
                    cursor.execute(search_query, (current_locked_cat, query_vector))
                    db_matches = cursor.fetchall()
                else:
                    search_query = """
                    SELECT p.base_product_id, p.name, p.category, p.description, p.customization_matrix
                    FROM catalog_embeddings c
                    JOIN products p ON c.base_product_id = p.base_product_id
                    ORDER BY c.embedding <=> %s::vector
                    LIMIT 10;
                    """
                    cursor.execute(search_query, (query_vector,))
                    db_matches = cursor.fetchall()
                    
                cursor.close()
                conn.close()
                
                inventory_context_string = ""
                if current_locked_cat == "Bespoke Fabrics":
                    inventory_context_string = (
                        "ITEM 1:\nID: fabric_merino_wool\nName: Premium Super 140s Australian Merino Wool\nCategory: Bespoke Fabrics\nDescription: Raw high-grade structural suiting wool yarn sold independently by the linear meter.\n----------------------------------------\n"
                        "ITEM 2:\nID: fabric_mulberry_silk\nName: Mulberry Silk Filament Blend\nCategory: Bespoke Fabrics\nDescription: Pure high-sheen lightweight traditional dress silk material cuts sold independently by the meter.\n----------------------------------------\n"
                        "ITEM 3:\nID: fabric_highland_tweed\nName: Highland Premium Tweed Weave\nCategory: Bespoke Fabrics\nDescription: Heavyset richly patterned premium autumn textile segments sold independently by the linear meter.\n----------------------------------------\n"
                    )
                else:
                    if not db_matches:
                        inventory_context_string = "No active products matching this specification sheet are currently loaded."
                    else:
                        if not SESSION_MEMORY[session_key]["active_category"]:
                            # pyrefly: ignore [bad-index]
                            SESSION_MEMORY[session_key]["active_category"] = db_matches[0]["category"]
                        for index, item in enumerate(db_matches, 1):
                            inventory_context_string += (
                                # pyrefly: ignore [bad-index]
                                f"ITEM {index}:\nID: {item['base_product_id']}\nName: {item['name']}\nCategory: {item['category']}\nDescription: {item['description']}\nMatrix: {json.dumps(item['customization_matrix'])}\n----------------------------------------\n"
                            )
                
                SESSION_MEMORY[session_key]["last_context_string"] = inventory_context_string
                
            except Exception as db_err:
                import traceback
                print("⚠️ DATABASE OR EMBEDDING HICCUP DETECTED:")
                traceback.print_exc()
                inventory_context_string = SESSION_MEMORY[session_key]["last_context_string"] or "Showroom catalog connection is running slowly."

    # 5. SAFE-FAIL ZONE B: Large Language Model Inference Completion Layer
    try:
        system_instruction = (
            "You are Marco, an elite, highly persuasive human fashion consultant, salesman, and structured bespoke stylist for 'Agent Boutique'.\n"
            "Your tone must be warm, sophisticated, conversational, and direct. Your layout presentation must be immaculate, avoiding overwhelming walls of text or raw asterisks '**'.\n\n"
            
            "⛔ ABSOLUTE CONTEXT PROTECTION & SCOPE GUARDRAILS:\n"
            "0. STRICT OFF-TOPIC REFUSAL: You are operating strictly as a transactional retail showroom companion. You are NOT an encyclopedia, general assistant, or school tutor. "
            "If the user asks about ANYTHING unrelated to our specific store catalog styles, materials, or fashion curation (including but not limited to history essays, K-pop groups like BTS, celebrity gossip, science, math, or coding), you MUST flatly decline. "
            "Respond instantly with: 'I am here exclusively as your personal stylist at Agent Boutique. Let's return to designing your premium apparel layers. What category can I help you map out today?' "
            "NEVER break character, never answer the off-topic prompt, and NEVER offer alternative assistance such as saying 'I'd be happy to help you learn more about that music group'. If the user repeats the off-topic question, repeat your refusal verbatim.\n\n"
            
            "CRITICAL PROTOCOLS & CORE RULES:\n"
            "1. NO HALLUCINATIONS OR FILLERS: You are STRICTLY permitted to speak ONLY about the exact product items provided in the data context below. Never invent product names, variants, or designs. "
            "If the user requests a specific number of items (e.g., 'give me 10 coats') and there are fewer items provided in the data context below, you must explicitly state: 'I can present our current collection of premium styles from the vault today.' Print ONLY the real items listed in the context. Never invent placeholder entries to meet a numerical quota.\n"
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
            "10. No talks on life, mental health, suiside or every possible topic that comes outside the scope of our website and the products, redirect the user into something related to our website, giving a message that you are just there to assist them with fashion\n"
            f"CURRENT LIVE DATA WINDOW (TOP TRACKED INVENTORY MATCHES):\n"
            f"{inventory_context_string}"
        )
        
        groq_messages = [{"role": "system", "content": system_instruction}]
        for past_message in SESSION_MEMORY[session_key]["messages"]:
            groq_messages.append(past_message)
        groq_messages.append({"role": "user", "content": user_input})
        
        # pyrefly: ignore [no-matching-overload]
        groq_response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=groq_messages,
            temperature=0.0
        )
        
        ai_reply = groq_response.choices[0].message.content
        
        SESSION_MEMORY[session_key]["messages"].append({"role": "user", "content": user_input})
        SESSION_MEMORY[session_key]["messages"].append({"role": "assistant", "content": ai_reply})
        
        if len(SESSION_MEMORY[session_key]["messages"]) > 8:
            SESSION_MEMORY[session_key]["messages"] = SESSION_MEMORY[session_key]["messages"][-8:]
            
        return {"reply": ai_reply}

    except Exception as api_err:
        import traceback
        print("⚠️ GROQ INFERENCE COMPLETION TIMEOUT OR OVERLOAD DETECTED:")
        traceback.print_exc()
        return {"reply": "My apologies. Our showroom digital connection experienced a brief cloud optimization delay. Could you please re-state your last request so I can map out your design parameters flawlessly?"}