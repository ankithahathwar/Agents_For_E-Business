import os
import json
import psycopg2
from dotenv import load_dotenv

# 1. Load the secret connection string from your hidden .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def seed_database():
    print("Connecting to your cloud PostgreSQL database...")
    # 2. Establish a handshake with the Neon cloud server
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 3. Create the products table structure
    # We use JSONB for the customization_matrix to hold all our micro-options easily!
    create_table_query = """
    CREATE TABLE IF NOT EXISTS products (
        base_product_id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(100),
        description TEXT,
        customization_matrix JSONB
    );
    """
    cursor.execute(create_table_query)
    print("Table 'products' created successfully (or already existed).")
    
    # 4. Read your local products.json file
    with open("products.json", "r") as file:
        products = json.load(file)
        
    # 5. Loop through each item and upload it to the cloud
    for prod in products:
        insert_query = """
        INSERT INTO products (base_product_id, name, category, description, customization_matrix)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (base_product_id) 
        DO UPDATE SET 
            name = EXCLUDED.name,
            category = EXCLUDED.category,
            description = EXCLUDED.description,
            customization_matrix = EXCLUDED.customization_matrix;
        """
        
        # We use json.dumps() to convert the Python dictionary back to a clean string for Postgres to read
        cursor.execute(insert_query, (
            prod["base_product_id"],
            prod["name"],
            prod["category"],
            prod["description"],
            json.dumps(prod["customization_matrix"])
        ))
        print(f"Successfully uploaded: {prod['name']}")
        
    # 6. Commit the changes and close the connection securely
    conn.commit()
    cursor.close()
    conn.close()
    print("\nDatabase seeding complete! Your vault is locked and filled.")

if __name__ == "__main__":
    seed_database()