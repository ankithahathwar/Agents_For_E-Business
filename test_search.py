# pyrefly: ignore [missing-import]
import os
# pyrefly: ignore [untyped-import]
import psycopg2
# pyrefly: ignore [untyped-import]
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from google import genai

# 1. Initialize our environment and the Gemini encoder
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
client = genai.Client()

def get_query_vector(text_to_search):
    """Translates the user's casual search phrase into a 3072-dimensional vector."""
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text_to_search
    )
    # pyrefly: ignore [unsupported-operation]
    return response.embeddings[0].values

def test_semantic_query(user_prompt):
    print(f"Analyzing search intent for: '{user_prompt}'...")
    # Convert search text to vector coordinates
    search_vector = get_query_vector(user_prompt)
    
    # Connect to PostgreSQL using RealDictCursor so rows behave like clean python dicts
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    
    # The <=> operator determines vector distance. 
    # (1 - distance) converts it into a clean 'Similarity Score' percentage!
    vector_search_query = """
    SELECT base_product_id, item_type, text_content, (1 - (embedding <=> %s::vector)) AS similarity_score
    FROM catalog_embeddings
    ORDER BY embedding <=> %s::vector
    LIMIT 3;
    """
    
    cursor.execute(vector_search_query, (search_vector, search_vector))
    hits = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return hits

if __name__ == "__main__":
    # --- CHOOSE YOUR TEST VIBE HERE ---
    sample_human_phrase = "I get hot easily and sweat a lot, need something for a warm destination look"
    
    results = test_semantic_query(sample_human_phrase)
    
    print("\n==============================================")
    print("        🤖 AI CONCEPT MATCH RESULTS             ")
    print("==============================================")
    
    for rank, hit in enumerate(results, 1):
        # pyrefly: ignore [bad-index]
        print(f"\nRANK #{rank} | Similarity Match: {hit['similarity_score'] * 100:.2f}%")
        # pyrefly: ignore [bad-index]
        print(f"Product ID Reference: {hit['base_product_id']}")
        # pyrefly: ignore [bad-index]
        print(f"Inventory Layer Type: {hit['item_type'].upper()}")
        # pyrefly: ignore [bad-index]
        print(f"Data Segment Read by AI:\n -> \"{hit['text_content']}\"")
        print("-" * 46)