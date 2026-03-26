import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
cur = conn.cursor()

try:
    # Delete prices first (foreign key constraint)
    cur.execute("""
        DELETE FROM prices WHERE product_id IN (
            SELECT id FROM products 
            WHERE name IN ('iPhone 15', 'Samsung Galaxy S24', 'MacBook Pro 16', 'iPad Air', 'AirPods Pro 2')
        )
    """)
    
    # Delete products
    cur.execute("""
        DELETE FROM products 
        WHERE name IN ('iPhone 15', 'Samsung Galaxy S24', 'MacBook Pro 16', 'iPad Air', 'AirPods Pro 2')
    """)
    
    conn.commit()
    
    # Verify deletion
    cur.execute("SELECT COUNT(*) FROM products")
    product_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM prices")
    price_count = cur.fetchone()[0]
    
    print(f"✓ Sample data removed successfully!")
    print(f"  Remaining Products: {product_count}")
    print(f"  Remaining Prices: {price_count}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()
