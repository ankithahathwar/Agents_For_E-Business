import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# 1. Load the secret database URL from your hidden .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Initialize the FastAPI app instance
app = FastAPI(title="Agents_For_E-Business Core Backend")

def get_db_connection():
    """Establishes a temporary connection handshake with the cloud Postgres server."""
    # We use RealDictCursor so Postgres returns rows as Python dictionaries instead of plain lists
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# Endpoint 1: The Health Check Route
@app.get("/")
def read_root():
    return {"status": "online", "message": "The Agents_For_E-Business backend engine is humming."}

# Endpoint 2: Fetch all core product names and categories for the storefront menu
@app.get("/api/products")
def get_all_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # We select everything except the massive customization matrix to keep this initial list fast and light
        cursor.execute("SELECT base_product_id, name, category, description FROM products;")
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# Endpoint 3: Fetch the complete deep hyper-customization matrix for a specific chosen item
@app.get("/api/products/{product_id}")
def get_single_product_matrix(product_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Pull the specific row matching the requested ID
        cursor.execute("SELECT * FROM products WHERE base_product_id = %s;", (product_id,))
        product = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not product:
            raise HTTPException(status_code=404, detail="The requested designer catalog item was not found.")
            
        return product
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")