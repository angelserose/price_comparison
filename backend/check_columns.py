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
cur.execute("SELECT * FROM products LIMIT 1")
cols = [desc[0] for desc in cur.description]
print('Product columns:', cols)

cur.execute("SELECT * FROM products LIMIT 2")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
