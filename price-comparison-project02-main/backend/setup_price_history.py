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

# Create trigger function for automatic price history tracking
trigger_func = """
CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS $func$
BEGIN
    IF OLD.price IS DISTINCT FROM NEW.price THEN
        INSERT INTO price_history (product_id, store_id, old_price, new_price)
        VALUES (NEW.product_id, NEW.store_id, OLD.price, NEW.price);
    END IF;
    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;
"""

cur.execute(trigger_func)
conn.commit()
print('✅ Trigger function created!')

# Create trigger on prices table
trigger = """
DROP TRIGGER IF EXISTS price_change_trigger ON prices;
CREATE TRIGGER price_change_trigger
AFTER UPDATE ON prices
FOR EACH ROW
EXECUTE FUNCTION log_price_change();
"""

cur.execute(trigger)
conn.commit()
print('✅ Trigger attached to prices table!')

# Verify all tables
cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")
tables = [row[0] for row in cur.fetchall()]
print(f'\n✅ Complete Database Schema:')
for table in tables:
    print(f'   • {table}')

cur.close()
conn.close()
print('\n✅ Database is now complete and powerful! 🚀')
