#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')
    cur = conn.cursor()
    
    # Read SQL file
    with open('insert_sample_data.sql', 'r') as f:
        sql = f.read()
    
    # Execute SQL
    cur.execute(sql)
    conn.commit()
    
    print("✓ Sample data added successfully!")
    
    # Show what was added
    cur.execute("SELECT COUNT(*) FROM products")
    products = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM prices")
    prices = cur.fetchone()[0]
    
    print(f"\n✓ Total Products: {products}")
    print(f"✓ Total Prices: {prices}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
