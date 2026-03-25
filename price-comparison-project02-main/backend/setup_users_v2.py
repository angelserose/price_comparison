import psycopg2
import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    sys.exit(1)

print(f"Connecting to database...")

try:
    # Try with SSL first (Supabase)
    conn = psycopg2.connect(db_url, sslmode='require', connect_timeout=5)
except Exception as e:
    print(f"⚠️  SSL connection failed, trying without SSL...")
    try:
        conn = psycopg2.connect(db_url, connect_timeout=5)
    except Exception as e2:
        print(f"❌ FATAL: Could not connect to database")
        print(f"Error: {str(e2)}")
        print(f"\n⚠️  Make sure:")
        print(f"    1. Mobile hotspot is ACTIVE")
        print(f"    2. DATABASE_URL in .env is correct")
        print(f"    3. Supabase project is running")
        sys.exit(1)

cur = conn.cursor()

print("✓ Connected to database\n")
print("Setting up database...\n")

try:
    # Hash passwords
    user_pass_hash = generate_password_hash('user@123')
    admin_pass_hash = generate_password_hash('admin@123')
    
    # Insert user with ON CONFLICT handling
    cur.execute("""
        INSERT INTO users (username, password) 
        VALUES ('user', %s)
        ON CONFLICT (username) DO UPDATE
        SET password = EXCLUDED.password
    """, (user_pass_hash,))
    
    print("  ✓ User 'user' / 'user@123' inserted/updated")
    
    # Insert admin with ON CONFLICT handling
    cur.execute("""
        INSERT INTO admin_users (username, password) 
        VALUES ('admin', %s)
        ON CONFLICT (username) DO UPDATE
        SET password = EXCLUDED.password
    """, (admin_pass_hash,))
    
    print("  ✓ Admin 'admin' / 'admin@123' inserted/updated")
    
    # Count products
    cur.execute("SELECT COUNT(*) FROM products")
    product_count = cur.fetchone()[0]
    print(f"  ✓ Total products in database: {product_count}")
    
    # Count prices
    cur.execute("SELECT COUNT(*) FROM prices")
    price_count = cur.fetchone()[0]
    print(f"  ✓ Total prices in database: {price_count}")
    
    # Count stores
    cur.execute("SELECT COUNT(*) FROM stores")
    store_count = cur.fetchone()[0]
    print(f"  ✓ Total stores in database: {store_count}")
    
    # Count users
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    print(f"  ✓ Total users in database: {user_count}")
    
    conn.commit()
    print("\n✅ Database setup complete!")
    
    if product_count == 0:
        print("\n⚠️  WARNING: No products found in database!")
        print("   You need to run the scraper: python scraper.py")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Error during setup: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    cur.close()
    conn.close()
