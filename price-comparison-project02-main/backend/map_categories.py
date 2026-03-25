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

# Get category IDs
cur.execute("SELECT category_id, category_name FROM categories")
categories = {name: cid for cid, name in cur.fetchall()}
print(f"Category mapping: {categories}\n")

# Map products to categories by keyword
mappings = [
    ('%iPhone%', 'Smartphones'),
    ('%Samsung%', 'Smartphones'),
    ('%MacBook%', 'Laptops'),
    ('%Dell%', 'Laptops'),
    ('%HP%', 'Laptops'),
    ('%Sony%', 'Electronics'),
    ('%iPad%', 'Electronics'),
    ('%TV%', 'Electronics'),
    ('%Watch%', 'Accessories'),
    ('%Mouse%', 'Accessories'),
    ('%Headphones%', 'Accessories'),
]

print("Mapping products to categories:")
for keyword, category_name in mappings:
    category_id = categories[category_name]
    cur.execute(f"UPDATE products SET category_id = {category_id} WHERE name ILIKE '{keyword}' AND category_id IS NULL")
    count = cur.rowcount
    if count > 0:
        print(f"  ✅ {keyword} → {category_name} ({count} products)")

conn.commit()

# Verify
print("\nProducts by Category:")
cur.execute("""
    SELECT c.category_name, COUNT(p.id) as count
    FROM categories c
    LEFT JOIN products p ON c.category_id = p.category_id
    GROUP BY c.category_name
    ORDER BY count DESC
""")

for cat_name, count in cur.fetchall():
    print(f"  • {cat_name}: {count}")

print("\n✅ Categories setup complete!")

cur.close()
conn.close()
