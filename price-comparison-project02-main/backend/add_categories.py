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

print("\n" + "="*60)
print("ADDING CATEGORIES TO DATABASE")
print("="*60 + "\n")

try:
    # Step 1: Create categories table
    print("Step 1: Creating categories table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id SERIAL PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL UNIQUE
        )
    """)
    conn.commit()
    print("✅ Categories table created\n")

    # Step 2: Add category_id column to products if it doesn't exist
    print("Step 2: Adding category_id column to products...")
    try:
        cur.execute("""
            ALTER TABLE products
            ADD COLUMN category_id INT
        """)
        conn.commit()
        print("✅ Column added to products\n")
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print("✅ Column already exists, skipping\n")
            conn.rollback()
        else:
            raise

    # Step 3: Add foreign key constraint
    print("Step 3: Adding foreign key constraint...")
    try:
        cur.execute("""
            ALTER TABLE products
            ADD CONSTRAINT fk_category
            FOREIGN KEY (category_id)
            REFERENCES categories(category_id)
            ON DELETE SET NULL
        """)
        conn.commit()
        print("✅ Foreign key constraint added\n")
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print("✅ Constraint already exists, skipping\n")
            conn.rollback()
        else:
            raise

    # Step 4: Insert sample categories
    print("Step 4: Inserting sample categories...")
    categories = ['Smartphones', 'Laptops', 'Electronics', 'Accessories']
    for category in categories:
        cur.execute(
            "INSERT INTO categories (category_name) VALUES (%s) ON CONFLICT (category_name) DO NOTHING",
            (category,)
        )
    conn.commit()
    print("✅ Categories inserted\n")

    # Step 5: Map products to categories (intelligent mapping)
    print("Step 5: Mapping products to categories...")
    
    product_category_map = {
        'iPhone': 'Smartphones',
        'Samsung': 'Smartphones',
        'MacBook': 'Laptops',
        'Dell XPS': 'Laptops',
        'HP Pavilion': 'Laptops',
        'Sony': 'Electronics',
        'Headphones': 'Accessories',
        'Apple Watch': 'Accessories',
        'iPad': 'Electronics',
        'TV': 'Electronics',
        'Mouse': 'Accessories'
    }
    
    for product_keyword, category_name in product_category_map.items():
        cur.execute("""
            UPDATE products
            SET category_id = (
                SELECT category_id FROM categories WHERE category_name = %s
            )
            WHERE product_name ILIKE %s AND category_id IS NULL
        """, (category_name, f'%{product_keyword}%'))
    
    conn.commit()
    print("✅ Products mapped to categories\n")

    # Verify the setup
    print("="*60)
    print("VERIFICATION")
    print("="*60 + "\n")

    # Count categories
    cur.execute("SELECT COUNT(*) FROM categories")
    cat_count = cur.fetchone()[0]
    print(f"Total categories: {cat_count}")

    # Show category distribution
    cur.execute("""
        SELECT c.category_name, COUNT(p.product_id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.category_id = p.category_id
        GROUP BY c.category_name
        ORDER BY product_count DESC
    """)
    
    print("\nProducts by Category:")
    for cat_name, count in cur.fetchall():
        print(f"  • {cat_name}: {count} products")

    # Show sample products with categories
    print("\nSample Products with Categories:")
    cur.execute("""
        SELECT p.product_name, c.category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LIMIT 10
    """)
    
    for product_name, category_name in cur.fetchall():
        cat_display = category_name if category_name else "Unassigned"
        print(f"  • {product_name}: {cat_display}")

    print("\n" + "="*60)
    print("✅ DATABASE ENHANCEMENT COMPLETE!")
    print("="*60 + "\n")
    print("Your database now supports:")
    print("  ✔ Product categorization")
    print("  ✔ Better data normalization")
    print("  ✔ Advanced filtering queries")
    print("  ✔ Category-based analytics\n")

except Exception as e:
    conn.rollback()
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

finally:
    cur.close()
    conn.close()
