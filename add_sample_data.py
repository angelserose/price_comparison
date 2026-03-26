import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')
cur = conn.cursor()

print("="*60)
print("DATABASE STATUS CHECK")
print("="*60)

# Check existing data
try:
    cur.execute("SELECT COUNT(*) FROM products")
    product_count = cur.fetchone()[0]
    print(f"\n✓ Products: {product_count}")
    
    cur.execute("SELECT COUNT(*) FROM stores")
    store_count = cur.fetchone()[0]
    print(f"✓ Stores: {store_count}")
    
    cur.execute("SELECT COUNT(*) FROM prices")
    price_count = cur.fetchone()[0]
    print(f"✓ Prices: {price_count}")
    
except Exception as e:
    print(f"✗ Error checking data: {e}")
    cur.close()
    conn.close()
    exit(1)

# If no products, add sample data
if product_count == 0:
    print("\n" + "="*60)
    print("ADDING SAMPLE DATA")
    print("="*60)
    
    try:
        # Insert stores
        cur.execute("INSERT INTO stores (store_name) VALUES ('Amazon'), ('Flipkart'), ('JioMart') ON CONFLICT DO NOTHING")
        
        # Insert sample products
        sample_products = [
            ('iPhone 15', 'https://via.placeholder.com/200?text=iPhone+15'),
            ('Samsung Galaxy S24', 'https://via.placeholder.com/200?text=Samsung+S24'),
            ('MacBook Pro', 'https://via.placeholder.com/200?text=MacBook+Pro'),
            ('iPad Air', 'https://via.placeholder.com/200?text=iPad+Air'),
            ('AirPods Pro', 'https://via.placeholder.com/200?text=AirPods'),
        ]
        
        for product_name, image_url in sample_products:
            cur.execute("INSERT INTO products (name, image_url) VALUES (%s, %s)", (product_name, image_url))
        
        conn.commit()
        print("✓ Products inserted")
        
        # Get product and store IDs
        cur.execute("SELECT id FROM products")
        product_ids = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT id FROM stores")
        store_ids = [row[0] for row in cur.fetchall()]
        
        # Insert sample prices
        prices_data = [
            (product_ids[0], store_ids[0], 79999.00, 89999.00, 20),      # iPhone 15 on Amazon
            (product_ids[0], store_ids[1], 82000.00, 89999.00, 18),      # iPhone 15 on Flipkart
            (product_ids[0], store_ids[2], 81500.00, 89999.00, 19),      # iPhone 15 on JioMart
            (product_ids[1], store_ids[0], 69999.00, 79999.00, 15),      # Samsung on Amazon
            (product_ids[1], store_ids[1], 71999.00, 79999.00, 10),      # Samsung on Flipkart
            (product_ids[2], store_ids[0], 199999.00, 229999.00, 15),    # MacBook on Amazon
            (product_ids[2], store_ids[2], 201999.00, 229999.00, 12),    # MacBook on JioMart
            (product_ids[3], store_ids[1], 54999.00, 64999.00, 15),      # iPad on Flipkart
            (product_ids[4], store_ids[0], 27999.00, 29999.00, 7),       # AirPods on Amazon
        ]
        
        for product_id, store_id, price, old_price, discount in prices_data:
            cur.execute("""
                INSERT INTO prices (product_id, store_id, price, old_price, store_url)
                VALUES (%s, %s, %s, %s, 'https://www.example.com')
            """, (product_id, store_id, price, old_price))
        
        conn.commit()
        print("✓ Prices inserted")
        
        print("\n✓ Sample data added successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error adding data: {e}")
        cur.close()
        conn.close()
        exit(1)

# Check final counts
print("\n" + "="*60)
print("FINAL STATUS")
print("="*60)

cur.execute("SELECT COUNT(*) FROM products")
print(f"✓ Products: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM prices")
print(f"✓ Prices: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM stores")
print(f"✓ Stores: {cur.fetchone()[0]}")

# Show sample products
print("\n" + "="*60)
print("SAMPLE PRODUCTS")
print("="*60)

cur.execute("""
    SELECT DISTINCT p.name, s.store_name, pr.price
    FROM prices pr
    JOIN products p ON pr.product_id = p.id
    JOIN stores s ON pr.store_id = s.id
    ORDER BY p.name, pr.price
    LIMIT 10
""")

for row in cur.fetchall():
    print(f"  {row[0]:<30} @ {row[1]:<15} ₹{row[2]:.2f}")

cur.close()
conn.close()

print("\n✓ Ready to refresh your app!")
print("Refresh the page in your browser to see products.")
