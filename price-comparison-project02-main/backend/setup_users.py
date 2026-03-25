import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()

# Insert test user
try:
    cur.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s) ON CONFLICT (username) DO UPDATE SET password=%s",
        ('user', 'user@123', 'user@123')
    )
    print("✓ User inserted/updated")
except Exception as e:
    print(f"User error: {e}")

# Insert test admin
try:
    cur.execute(
        "INSERT INTO admin_users (username, password) VALUES (%s, %s) ON CONFLICT (username) DO UPDATE SET password=%s",
        ('admin', 'admin@123', 'admin@123')
    )
    print("✓ Admin inserted/updated")
except Exception as e:
    print(f"Admin error: {e}")

conn.commit()

# Check if products exist
try:
    cur.execute("SELECT COUNT(*) FROM products")
    count = cur.fetchone()[0]
    print(f"✓ Total products in database: {count}")
    
    if count == 0:
        print("WARNING: No products found! Need to run scraper.py")
    
    cur.execute("SELECT COUNT(*) FROM prices")
    price_count = cur.fetchone()[0]
    print(f"✓ Total prices in database: {price_count}")
    
except Exception as e:
    print(f"Error checking products: {e}")

cur.close()
conn.close()

print("\n✓ Database setup complete!")
