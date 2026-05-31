# pyrefly: ignore [missing-import]
import os
import json
import psycopg2
from dotenv import load_dotenv
from google import genai

# 1. Pull the cloud credentials and Gemini keys from your safe .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Fire up the official Google GenAI Client
client = genai.Client()

def create_embeddings_table(cursor):
    """Drops the old mismatched table and builds a fresh 3072-dimensional slot."""
    # We clear out the old 768-dimension table if it exists to reset the structure clean
    cursor.execute("DROP TABLE IF EXISTS catalog_embeddings;")
    
    # We use VECTOR(3072) to perfectly match Gemini Embedding 2's default layout
    create_table_query = """
    CREATE TABLE catalog_embeddings (
        id SERIAL PRIMARY KEY,
        base_product_id VARCHAR(50),
        item_type VARCHAR(50), -- Tracks if the vector represents a 'product' or a 'fabric'
        text_content TEXT,
        embedding VECTOR(3072)
    );
    """
    cursor.execute(create_table_query)
    print("Table 'catalog_embeddings' successfully configured for 3072 dimensions.")

def get_gemini_vector(text_to_embed):
    """Sends raw text over to Google's supercomputers and fetches the 3072 floating numbers."""
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text_to_embed
    )
    return response.embeddings[0].values

def process_and_vectorize_catalog():
    print("Connecting to cloud database vault...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Re-build our destination AI table inside Postgres with 3072 dimensions
    create_embeddings_table(cursor)
    
    # 3. Pull your seeded products out of the relational table
    cursor.execute("SELECT base_product_id, name, category, description, customization_matrix FROM products;")
    products = cursor.fetchall()
    
    print(f"\nFound {len(products)} custom products in vault. Launching Gemini vectorization...")
    
    for row in products:
        b_id, name, category, description, matrix = row
        matrix_data = json.loads(matrix) if isinstance(matrix, str) else matrix
        
        # --- PHASE A: Vectorize the Core Product Story ---
        product_chunk = f"Product profile: {name}. Style Classification: {category}. Narrative Overview: {description}"
        print(f" -> Generating Gemini vector for primary item: {name}")
        product_vector = get_gemini_vector(product_chunk)
        
        cursor.execute(
            "INSERT INTO catalog_embeddings (base_product_id, item_type, text_content, embedding) VALUES (%s, %s, %s, %s);",
            (b_id, 'product', product_chunk, product_vector)
        )
        
        # --- PHASE B: Vectorize individual hidden fabric textures ---
        if "fabrics" in matrix_data:
            for fabric in matrix_data["fabrics"]:
                fabric_name = fabric.get("name", "")
                texture = fabric.get("texture", "")
                weight = fabric.get("weight", "")
                
                fabric_chunk = (
                    f"Fabric choice for {name}: {fabric_name}. "
                    f"Sensory texture details: {texture} "
                    f"Material Weight indicator: {weight}."
                )
                
                print(f"    -> Generating Gemini vector for fabric element: {fabric_name}")
                fabric_vector = get_gemini_vector(fabric_chunk)
                
                cursor.execute(
                    "INSERT INTO catalog_embeddings (base_product_id, item_type, text_content, embedding) VALUES (%s, %s, %s, %s);",
                    (b_id, 'fabric', fabric_chunk, fabric_vector)
                )
                
    # Commit your changes permanently to the cloud and lock the doors
    conn.commit()
    cursor.close()
    conn.close()
    print("\nVector pipeline complete! Your single Postgres vault now holds relational rows AND AI vectors.")

if __name__ == "__main__":
    process_and_vectorize_catalog()