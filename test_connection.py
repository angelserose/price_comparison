#!/usr/bin/env python3
"""
Database Connection Test Script
Tests connectivity to Supabase PostgreSQL database
Run this before deployment to verify everything is configured correctly
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql, Error

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("SNAP Database Connection Test")
    print("=" * 60)
    
    # Get Database URL
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        print("\n📝 Create .env file with:")
        print("   DATABASE_URL=postgresql://postgres:PASSWORD@db.supabase.co:5432/postgres")
        return False
    
    print("\n✓ DATABASE_URL found")
    print(f"   URL: {database_url[:50]}...")  # Hide password
    
    # Try connection with SSL
    print("\n[1/5] Attempting connection with SSL...")
    try:
        conn = psycopg2.connect(database_url, sslmode='require')
        print("✓ Connected with SSL")
        ssl_mode = 'require'
    except Error as e:
        print(f"⚠ SSL connection failed: {e}")
        print("[2/5] Attempting connection without SSL...")
        try:
            conn = psycopg2.connect(database_url)
            print("✓ Connected without SSL")
            ssl_mode = 'disabled'
        except Error as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    try:
        # Create cursor
        print("\n[3/5] Creating database cursor...")
        cur = conn.cursor()
        print("✓ Cursor created")
        
        # Test basic query
        print("\n[4/5] Running test query...")
        cur.execute("SELECT 1 as test")
        result = cur.fetchone()
        print(f"✓ Query successful: {result}")
        
        # Check tables
        print("\n[5/5] Checking database tables...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        if not tables:
            print("⚠ WARNING: No tables found in database")
            print("   Run setup.sql to create tables")
        else:
            print(f"✓ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
                
                # Count rows in each table
                try:
                    cur.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(table)
                    ))
                    count = cur.fetchone()[0]
                    print(f"     Rows: {count}")
                except Exception as e:
                    print(f"     Error counting rows: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("CONNECTION TEST SUMMARY")
        print("=" * 60)
        print(f"✓ SSL Mode: {ssl_mode}")
        print(f"✓ Tables: {len(tables)}")
        print("✓ Database: Ready for deployment!")
        print("=" * 60)
        
        cur.close()
        return True
        
    except Error as e:
        print(f"\n❌ Error during test: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Main function"""
    print("\n")
    success = test_connection()
    
    if success:
        print("\n✅ All tests passed! Your database is ready.\n")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Fix issues before deploying.\n")
        print("Troubleshooting:")
        print("1. Verify .env file exists with DATABASE_URL")
        print("2. Check Supabase project is running")
        print("3. Verify database credentials are correct")
        print("4. Test manually in Supabase SQL Editor")
        sys.exit(1)

if __name__ == '__main__':
    main()
