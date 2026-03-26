import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DATABASE_URL')
try:
    conn = psycopg2.connect(db_url, sslmode='require', connect_timeout=5)
except:
    conn = psycopg2.connect(db_url, connect_timeout=5)

cur = conn.cursor()

# Get all tables
cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")

tables = cur.fetchall()
print(f'\n========== DATABASE TABLES ==========')
print(f'Total Tables: {len(tables)}\n')

for i, (table_name,) in enumerate(tables, 1):
    # Get row count for each table
    cur.execute(f'SELECT COUNT(*) FROM {table_name}')
    row_count = cur.fetchone()[0]
    print(f'{i}. {table_name:20} ({row_count} rows)')

print(f'\n======================================\n')

cur.close()
conn.close()
