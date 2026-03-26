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

# Step 1: Create categories table
cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id SERIAL PRIMARY KEY,
        category_name VARCHAR(100) NOT NULL UNIQUE
    )
""")

# Step 2: Add category_id column to products if it doesn't exist
try:
    cur.execute("ALTER TABLE products ADD COLUMN category_id INT")
except:
    pass

# Step 3: Add foreign key constraint
try:
    cur.execute("""
        ALTER TABLE products
        ADD CONSTRAINT fk_category
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL
    """)
except:
    pass

# Step 4: Insert sample categories
cur.execute("INSERT INTO categories (category_name) VALUES ('Smartphones') ON CONFLICT (category_name) DO NOTHING")
cur.execute("INSERT INTO categories (category_name) VALUES ('Laptops') ON CONFLICT (category_name) DO NOTHING")
cur.execute("INSERT INTO categories (category_name) VALUES ('Electronics') ON CONFLICT (category_name) DO NOTHING")
cur.execute("INSERT INTO categories (category_name) VALUES ('Accessories') ON CONFLICT (category_name) DO NOTHING")

conn.commit()  # Commit categories before using them

# Step 5: Map products to categories
cur.execute("UPDATE products SET category_id = 1 WHERE name ILIKE '%iPhone%' AND category_id IS NULL")
cur.execute("UPDATE products SET category_id = 1 WHERE name ILIKE '%Samsung%' AND category_id IS NULL")
cur.execute("UPDATE products SET category_id = 2 WHERE name ILIKE '%MacBook%' AND category_id IS NULL")
cur.execute("UPDATE products SET category_id = 2 WHERE name ILIKE '%Dell%' AND category_id IS NULL")
cur.execute("UPDATE products SET category_id = 2 WHERE name ILIKE '%HP%' AND category_id IS NULL")
cur.execute("UPDATE products SET category_id = 3 WHERE name ILIKE '%Sony%' AND category_id IS NULL")
cur.execute("UPDATE products SET category_id = 3 WHERE name ILIKE '%iPad%' AND category_id IS NULL")
cur.execute("UPDATE products SET category_id = 3 WHERE name ILIKE '%TV%' AND category_id IS NULL")
cur.execute("UPDATE products SET category_id = 4 WHERE name ILIKE '%Watch%' AND category_id IS NULL")
cur.execute("UPDATE products SET category_id = 4 WHERE name ILIKE '%Mouse%' AND category_id IS NULL")
cur.execute("UPDATE products SET category_id = 4 WHERE name ILIKE '%Headphones%' AND category_id IS NULL")

conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM categories")
print(f"✅ Categories created: {cur.fetchone()[0]}")

cur.execute("""
    SELECT c.category_name, COUNT(p.product_id)
    FROM categories c
    LEFT JOIN products p ON c.category_id = p.category_id
    GROUP BY c.category_name
""")

print("\nProducts by Category:")
for cat, count in cur.fetchall():
    print(f"  • {cat}: {count}")

cur.close()
conn.close()
print("\n✅ Categories setup complete!")
