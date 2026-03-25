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
print("ADDING SALES/DISCOUNT FEATURE TO PRICES TABLE")
print("="*60 + "\n")

try:
    # Step 1: Add sale columns to prices table
    print("Step 1: Adding sale columns to prices table...")
    try:
        cur.execute("""
            ALTER TABLE prices
            ADD COLUMN original_price DECIMAL(10,2),
            ADD COLUMN discount_percent INT,
            ADD COLUMN is_on_sale BOOLEAN DEFAULT FALSE
        """)
        conn.commit()
        print("✅ Sale columns added\n")
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print("✅ Columns already exist, skipping\n")
            conn.rollback()
        else:
            raise

    # Step 2: Add sample sale data
    print("Step 2: Adding sample sale data...")
    
    # Get product and store IDs
    cur.execute("SELECT id FROM products WHERE name ILIKE '%iPhone%' LIMIT 1")
    iphone_id = cur.fetchone()[0] if cur.rowcount > 0 else None
    
    cur.execute("SELECT id FROM products WHERE name ILIKE '%Samsung%' LIMIT 1")
    samsung_id = cur.fetchone()[0] if cur.rowcount > 0 else None
    
    cur.execute("SELECT id FROM products WHERE name ILIKE '%MacBook%' LIMIT 1")
    macbook_id = cur.fetchone()[0] if cur.rowcount > 0 else None
    
    # Get store IDs
    cur.execute("SELECT id, store_name FROM stores")
    stores = {name: sid for sid, name in cur.fetchall()}
    
    # Add sale data
    sales_updates = [
        # (product_id, store_id, original_price, sale_price, discount_percent)
        (iphone_id, stores.get('Amazon'), 80000, 75000, 6),
        (iphone_id, stores.get('Flipkart'), 78000, 72000, 8),
        (samsung_id, stores.get('Amazon'), 75000, 69000, 8),
        (macbook_id, stores.get('Flipkart'), 97999, 87999, 10),
    ]
    
    for product_id, store_id, original, sale_price, discount in sales_updates:
        if product_id and store_id:
            cur.execute("""
                UPDATE prices
                SET original_price = %s,
                    discount_percent = %s,
                    is_on_sale = TRUE
                WHERE product_id = %s AND store_id = %s
            """, (original, discount, product_id, store_id))
            if cur.rowcount > 0:
                # Also update the price field
                cur.execute("""
                    UPDATE prices
                    SET price = %s
                    WHERE product_id = %s AND store_id = %s
                """, (sale_price, product_id, store_id))
                print(f"  ✅ Added {discount}% sale for product {product_id} at store {store_id}")
    
    conn.commit()
    print("")

    # Step 3: Show sale products
    print("="*60)
    print("CURRENT SALE PRODUCTS")
    print("="*60 + "\n")
    
    cur.execute("""
        SELECT p.name, s.store_name, pr.price, pr.original_price, pr.discount_percent
        FROM prices pr
        JOIN products p ON pr.product_id = p.id
        JOIN stores s ON pr.store_id = s.id
        WHERE pr.is_on_sale = TRUE
        ORDER BY pr.discount_percent DESC
    """)
    
    sales = cur.fetchall()
    if sales:
        print(f"{'Product':<30} {'Store':<12} {'Sale Price':>12} {'Original':>12} {'Discount':>10}")
        print("-" * 80)
        for product, store, sale_price, original, discount in sales:
            print(f"{product:<30} {store:<12} ₹{sale_price:>10.0f}  ₹{original:>10.0f}  {discount:>8}%")
    else:
        print("No products on sale yet!")
    
    # Step 4: Show financial impact
    print("\n" + "="*60)
    print("SALE ANALYTICS")
    print("="*60 + "\n")
    
    cur.execute("""
        SELECT 
            COUNT(*) as sale_count,
            ROUND(AVG(discount_percent)::numeric, 1) as avg_discount,
            MAX(discount_percent) as max_discount,
            MIN(discount_percent) as min_discount
        FROM prices
        WHERE is_on_sale = TRUE
    """)
    
    count, avg_disc, max_disc, min_disc = cur.fetchone()
    print(f"Total products on sale: {count}")
    print(f"Average discount: {avg_disc}%")
    print(f"Max discount: {max_disc}%")
    print(f"Min discount: {min_disc}%")
    
    print("\n" + "="*60)
    print("✅ SALES FEATURE IMPLEMENTED!")
    print("="*60)
    print("\nYour schema now includes:")
    print("  ✔ Categories")
    print("  ✔ Products")
    print("  ✔ Stores")
    print("  ✔ Prices with Sales/Discounts")
    print("  ✔ Price History (automatic tracking)")
    print("\nYou can now:")
    print("  • Show discounted prices on website")
    print("  • Highlight best deals")
    print("  • Track price changes with sales")
    print("  • Analytics on discount trends\n")

except Exception as e:
    conn.rollback()
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

finally:
    cur.close()
    conn.close()
