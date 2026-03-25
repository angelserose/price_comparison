import os
import psycopg2
from dotenv import load_dotenv
import sys
import socket

load_dotenv()

db_url = os.environ.get('DATABASE_URL')

print(f"Testing connection...")
print(f"URL: {db_url[:50]}...\n")

# Try to resolve the hostname
try:
    print("Resolving hostname...")
    address_info = socket.getaddrinfo('db.iruysnusweouqqmvmwtq.supabase.co', 5432, socket.AF_UNSPEC, socket.SOCK_STREAM)
    print(f"Address info: {address_info}\n")
except Exception as e:
    print(f"DNS resolution error: {e}\n")

# Try connection with various options
try:
    print("Attempting psycopg2 connection with sslmode='require'...")
    conn = psycopg2.connect(
        db_url,
        sslmode='require',
        connect_timeout=10
    )
    print("✓ Connected successfully!")
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print(f"✓ Query executed: {cur.fetchone()}")
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    
    # Try without sslmode
    print("\nTrying without sslmode requirement...")
    try:
        conn = psycopg2.connect(
            'postgresql://postgres:5x6lkGsowSSPr89n@db.iruysnusweouqqmvmwtq.supabase.co:5432/postgres',
            connect_timeout=10
        )
        print("✓ Connected without SSL!")
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        print(f"✓ Query executed: {cur.fetchone()}")
        cur.close()
        conn.close()
    except Exception as e2:
        print(f"✗ Still failed: {e2}")
