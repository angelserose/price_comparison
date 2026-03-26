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
print("\n" + "="*50)
print("PostgreSQL Interactive Terminal")
print("="*50)
print("Type your SQL queries below (type 'exit' to quit)")
print("="*50 + "\n")

while True:
    try:
        sql = input("sql> ").strip()
        
        if sql.lower() == 'exit':
            print("Closing connection...")
            break
        
        if not sql:
            continue
        
        cur.execute(sql)
        
        # If it's a SELECT query, fetch and print results
        if sql.upper().startswith('SELECT'):
            results = cur.fetchall()
            if results:
                # Print column names
                col_names = [desc[0] for desc in cur.description]
                print("\n" + " | ".join(col_names))
                print("-" * 80)
                for row in results:
                    print(" | ".join(str(x) for x in row))
                print(f"\nRows: {len(results)}\n")
            else:
                print("(No results)\n")
        else:
            conn.commit()
            print(f"✓ Query executed successfully\n")
    
    except Exception as e:
        print(f"Error: {str(e)}\n")

cur.close()
conn.close()
print("✓ Connection closed")
