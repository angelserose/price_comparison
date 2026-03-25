import os
import psycopg2
from dotenv import load_dotenv
import sys

load_dotenv()

db_url = os.environ.get('DATABASE_URL')

print(f"Testing connection with DATABASE_URL...")

if not db_url:
    print("ERROR: DATABASE_URL not found in .env file")
    sys.exit(1)

print(f"URL (first 50 chars): {db_url[:50]}...")

try:
    print("Attempting to connect...")
    conn = psycopg2.connect(
        db_url,
        sslmode='require',
        connect_timeout=10
    )
    print("✓ Connected to Supabase successfully!")
    
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    result = cur.fetchone()
    print(f"✓ Query executed successfully! Result: {result}")
    
    cur.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"✗ Connection Operational Error: {e}")
    sys.exit(1)
except psycopg2.DatabaseError as e:
    print(f"✗ Database Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected Error: {type(e).__name__}: {e}")
    sys.exit(1)