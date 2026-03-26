import os
import psycopg2
import socket
from dotenv import load_dotenv
import sys

load_dotenv()
db_url = os.environ.get('DATABASE_URL')

print(f"Testing connection with IPv4 workaround...\n")

# Parse the connection string and get the IP address directly
hostname = "db.iruysnusweouqqmvmwtq.supabase.co"

# Get IPv6 address from DNS
try:
    ipv6_addr = socket.getaddrinfo(hostname, 5432, socket.AF_INET6, socket.SOCK_STREAM)[0][4][0]
    print(f"IPv6 address: {ipv6_addr}")
    
    # Try connecting with IPv6 address directly
    print(f"\nAttempting connection with IPv6 address...")
    connection_string = f"postgresql://postgres:8Twh8Rn52PtSnFWZ@[{ipv6_addr}]:5432/postgres"
    print(f"URL: postgresql://postgres:***@[{ipv6_addr}]:5432/postgres")
    
    conn = psycopg2.connect(
        connection_string,
        sslmode='require',
        connect_timeout=10
    )
    print("✓ Connected successfully with IPv6!")
    
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print(f"✓ Query executed: {cur.fetchone()}")
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ IPv6 connection failed: {type(e).__name__}: {e}\n")
    
    # Try simple approach
    print("Trying simple direct connection without workarounds...")
    try:
        conn = psycopg2.connect(db_url, sslmode='require', connect_timeout=10)
        print("✓ Connected!")
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        print(f"✓ Query: {cur.fetchone()}")
        cur.close()
        conn.close()
    except Exception as e2:
        print(f"✗ Failed: {e2}")
