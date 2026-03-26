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

# Check categories table
cur.execute("SELECT * FROM categories")
cats = cur.fetchall()
print(f"Categories in database: {len(cats)}")
for cat in cats:
    print(f"  {cat}")

if len(cats) == 0:
    print("\nInserting categories now...")
    cur.execute("INSERT INTO categories (category_name) VALUES ('Smartphones')")
    cur.execute("INSERT INTO categories (category_name) VALUES ('Laptops')")
    cur.execute("INSERT INTO categories (category_name) VALUES ('Electronics')")
    cur.execute("INSERT INTO categories (category_name) VALUES ('Accessories')")
    conn.commit()
    print("✅ Categories inserted")

cur.close()
conn.close()
