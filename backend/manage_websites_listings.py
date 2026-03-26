import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Database connection
db_url = os.environ.get('DATABASE_URL')

try:
    conn = psycopg2.connect(db_url, sslmode='require', connect_timeout=5)
except Exception as e:
    print(f"SSL connection failed, trying without SSL: {e}")
    try:
        conn = psycopg2.connect(db_url)
    except Exception as e2:
        print(f"Connection failed: {e2}")
        raise

cur = conn.cursor()

def create_tables():
    """Create websites and listing tables"""
    try:
        # Create websites table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS websites (
                site_id SERIAL PRIMARY KEY,
                site_name VARCHAR(255) NOT NULL UNIQUE,
                site_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create listing table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS listing (
                listing_id SERIAL PRIMARY KEY,
                site_id INT NOT NULL REFERENCES websites(site_id) ON DELETE CASCADE,
                product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                product_url TEXT NOT NULL,
                current_price DECIMAL(10, 2),
                availability_status VARCHAR(50) DEFAULT 'In Stock',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(product_id, site_id)
            )
        """)

        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_listing_site_id ON listing(site_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_listing_product_id ON listing(product_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_listing_availability ON listing(availability_status)")

        # Insert sample websites
        cur.execute("""
            INSERT INTO websites (site_name, site_url) VALUES 
                ('Amazon', 'https://www.amazon.com'),
                ('Flipkart', 'https://www.flipkart.com'),
                ('JioMart', 'https://www.jiomart.com')
            ON CONFLICT (site_name) DO NOTHING
        """)

        conn.commit()
        print("✓ Tables created successfully!")
        print("✓ Sample websites inserted!")

    except Exception as e:
        conn.rollback()
        print(f"Error creating tables: {e}")

def show_websites():
    """Display all websites"""
    try:
        cur.execute("SELECT site_id, site_name, site_url, created_at FROM websites ORDER BY site_id")
        websites = cur.fetchall()
        
        if websites:
            print("\n" + "="*80)
            print("WEBSITES TABLE")
            print("="*80)
            print(f"{'Site ID':<10} {'Site Name':<20} {'Site URL':<40} {'Created At':<15}")
            print("-"*80)
            for site in websites:
                print(f"{site[0]:<10} {site[1]:<20} {site[2]:<40} {str(site[3])[:15]:<15}")
            print("="*80)
        else:
            print("No websites found!")
    except Exception as e:
        print(f"Error: {e}")

def show_listings():
    """Display all listings with related website and product info"""
    try:
        cur.execute("""
            SELECT 
                l.listing_id,
                w.site_name,
                p.name,
                l.product_url,
                l.current_price,
                l.availability_status,
                l.last_updated
            FROM listing l
            JOIN websites w ON l.site_id = w.site_id
            JOIN products p ON l.product_id = p.id
            ORDER BY l.listing_id
        """)
        listings = cur.fetchall()
        
        if listings:
            print("\n" + "="*120)
            print("LISTINGS TABLE")
            print("="*120)
            print(f"{'ID':<8} {'Site':<15} {'Product':<25} {'URL':<35} {'Price':<12} {'Status':<12} {'Last Updated':<15}")
            print("-"*120)
            for listing in listings:
                product_name = listing[2][:24] if len(listing[2]) > 24 else listing[2]
                url = listing[3][:34] if len(listing[3]) > 34 else listing[3]
                print(f"{listing[0]:<8} {listing[1]:<15} {product_name:<25} {url:<35} ${listing[4]:<11} {listing[5]:<12} {str(listing[6])[:14]:<15}")
            print("="*120)
        else:
            print("No listings found!")
    except Exception as e:
        print(f"Error: {e}")

def add_website(site_name, site_url):
    """Add a new website"""
    try:
        cur.execute(
            "INSERT INTO websites (site_name, site_url) VALUES (%s, %s) RETURNING site_id, site_name",
            (site_name, site_url)
        )
        result = cur.fetchone()
        conn.commit()
        print(f"✓ Website added! ID: {result[0]}, Name: {result[1]}")
    except psycopg2.IntegrityError:
        conn.rollback()
        print(f"✗ Website '{site_name}' already exists!")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

def add_listing(site_id, product_id, product_url, current_price, availability_status):
    """Add a new listing"""
    try:
        cur.execute(
            """
            INSERT INTO listing (site_id, product_id, product_url, current_price, availability_status, last_updated)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING listing_id
            """,
            (site_id, product_id, product_url, current_price, availability_status)
        )
        result = cur.fetchone()
        conn.commit()
        print(f"✓ Listing added! ID: {result[0]}")
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "duplicate key" in str(e):
            print(f"✗ Listing for this product and site already exists!")
        else:
            print(f"✗ Error: {e}")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

def update_listing_price(listing_id, new_price, availability_status):
    """Update listing price and availability"""
    try:
        cur.execute(
            """
            UPDATE listing 
            SET current_price = %s, availability_status = %s, last_updated = CURRENT_TIMESTAMP
            WHERE listing_id = %s
            """,
            (new_price, availability_status, listing_id)
        )
        conn.commit()
        print(f"✓ Listing {listing_id} updated!")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

def get_listings_by_site(site_name):
    """Get all listings for a specific site"""
    try:
        cur.execute("""
            SELECT 
                l.listing_id,
                p.name,
                l.product_url,
                l.current_price,
                l.availability_status,
                l.last_updated
            FROM listing l
            JOIN websites w ON l.site_id = w.site_id
            JOIN products p ON l.product_id = p.id
            WHERE w.site_name = %s
            ORDER BY l.listing_id
        """, (site_name,))
        
        listings = cur.fetchall()
        if listings:
            print(f"\n{'='*100}")
            print(f"Listings from {site_name}")
            print(f"{'='*100}")
            print(f"{'ID':<8} {'Product':<30} {'Price':<12} {'Status':<15} {'Last Updated':<20}")
            print("-"*100)
            for listing in listings:
                product_name = listing[1][:29] if len(listing[1]) > 29 else listing[1]
                print(f"{listing[0]:<8} {product_name:<30} ${listing[3]:<11} {listing[4]:<15} {str(listing[5]):<20}")
            print(f"{'='*100}")
        else:
            print(f"No listings found for {site_name}")
    except Exception as e:
        print(f"Error: {e}")

def main_menu():
    """Main menu for database operations"""
    while True:
        print("\n" + "="*60)
        print("WEBSITES & LISTINGS MANAGEMENT")
        print("="*60)
        print("1. Create Tables")
        print("2. Show All Websites")
        print("3. Show All Listings")
        print("4. Add Website")
        print("5. Add Listing")
        print("6. Update Listing Price")
        print("7. Get Listings by Site")
        print("8. Exit")
        print("="*60)
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == "1":
            create_tables()
        elif choice == "2":
            show_websites()
        elif choice == "3":
            show_listings()
        elif choice == "4":
            site_name = input("Enter site name: ").strip()
            site_url = input("Enter site URL: ").strip()
            add_website(site_name, site_url)
        elif choice == "5":
            try:
                site_id = int(input("Enter site ID: ").strip())
                product_id = int(input("Enter product ID: ").strip())
                product_url = input("Enter product URL: ").strip()
                current_price = float(input("Enter current price: ").strip())
                availability_status = input("Enter availability status (default: In Stock): ").strip() or "In Stock"
                add_listing(site_id, product_id, product_url, current_price, availability_status)
            except ValueError:
                print("Invalid input!")
        elif choice == "6":
            try:
                listing_id = int(input("Enter listing ID: ").strip())
                new_price = float(input("Enter new price: ").strip())
                availability_status = input("Enter availability status: ").strip()
                update_listing_price(listing_id, new_price, availability_status)
            except ValueError:
                print("Invalid input!")
        elif choice == "7":
            site_name = input("Enter site name: ").strip()
            get_listings_by_site(site_name)
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    print("Initializing database connection...")
    try:
        create_tables()
        show_websites()
        main_menu()
    finally:
        cur.close()
        conn.close()
        print("\nDatabase connection closed.")
