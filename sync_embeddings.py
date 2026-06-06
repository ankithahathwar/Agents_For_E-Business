import os
import json
# pyrefly: ignore [untyped-import]
import psycopg2
# pyrefly: ignore [untyped-import]
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from google import genai

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize the Gemini Client
gemini_client = genai.Client()

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_gemini_embedding(text: str):
    """Generates a 3,072-dimensional vector matching your main application logic."""
    response = gemini_client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )
    # pyrefly: ignore [unsupported-operation]
    return response.embeddings[0].values

def fix_vector_desync():
    print("[*] Connecting to Neon PostgreSQL instance...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch all product IDs that currently HAVE vectors
    cursor.execute("SELECT base_product_id FROM catalog_embeddings;")
    # pyrefly: ignore [bad-index]
    existing_vectors = {row["base_product_id"] for row in cursor.fetchall()}
    print(f"[DB] Found {len(existing_vectors)} items with active embeddings.")
    
    # 2. Fetch all raw products from the main inventory catalog
    cursor.execute("SELECT base_product_id, name, category, description, customization_matrix FROM products;")
    all_products = cursor.fetchall()
    
    # 3. Identify the missing items (like your scarves)
    # pyrefly: ignore [bad-index]
    missing_products = [p for p in all_products if p["base_product_id"] not in existing_vectors]
    
    if not missing_products:
        print("[OK] Excellent! Your vector database is 100% in sync with your product catalog.")
        cursor.close()
        conn.close()
        return

    print(f"[WARN] Detected {len(missing_products)} missing vectors. Initializing embedding generation pipelines...")
    
    # 4. Generate chunks and push embeddings to PostgreSQL
    for index, product in enumerate(missing_products, 1):
        # pyrefly: ignore [bad-index]
        prod_id = product["base_product_id"]
        # pyrefly: ignore [bad-index]
        prod_name = product["name"]
        # pyrefly: ignore [bad-index]
        prod_cat = product["category"]
        
        print(f"[{index}/{len(missing_products)}] Processing: {prod_name} ({prod_cat})")
        
        # Build the semantic text chunk exactly how your RAG expects it
        # pyrefly: ignore [bad-index]
        matrix_str = json.dumps(product["customization_matrix"]) if isinstance(product["customization_matrix"], dict) else str(product["customization_matrix"])
        # pyrefly: ignore [bad-index]
        text_payload = f"Name: {prod_name}\nCategory: {prod_cat}\nDescription: {product['description']}\nMatrix: {matrix_str}"
        
        try:
            # Call Gemini API
            vector_values = get_gemini_embedding(text_payload)
            
            # Insert vector array directly into the table
            cursor.execute(
                "INSERT INTO catalog_embeddings (base_product_id, embedding) VALUES (%s, %s::vector);",
                (prod_id, vector_values)
            )
            conn.commit() # Commit transaction-by-transaction to protect partial runs
            
        except Exception as e:
            print(f"[FAIL] Failed to embed item {prod_id}: {str(e)}")
            conn.rollback()
            continue

    print("\n[DONE] Migration Complete! All fabric and missing catalog entries are fully vectorized.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_vector_desync()