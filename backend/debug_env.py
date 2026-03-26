import os
from dotenv import load_dotenv, find_dotenv

# Find and load .env
dotenv_path = find_dotenv()
print(f"Looking for .env at: {dotenv_path}")

load_dotenv()

# Check if DATABASE_URL is loaded
db_url = os.environ.get('DATABASE_URL')
if db_url:
    print(f"✓ DATABASE_URL found: {db_url[:50]}...")
else:
    print("✗ DATABASE_URL not found in environment")
    
# List all environment variables
print("\nEnvironment variables from .env:")
for key, value in os.environ.items():
    if key in ['DATABASE_URL', 'SECRET_KEY', 'FLASK_ENV']:
        print(f"{key} = {value[:30]}..." if len(value) > 30 else f"{key} = {value}")
