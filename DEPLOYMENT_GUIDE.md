# Complete Deployment Guide: SNAP Price Comparison System
## Render + Supabase Deployment

---

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Part 1: Prepare Your Flask Project](#part-1-prepare-your-flask-project)
3. [Part 2: Set Up Supabase Database](#part-2-set-up-supabase-database)
4. [Part 3: Connect Flask to Supabase](#part-3-connect-flask-to-supabase)
5. [Part 4: Push Project to GitHub](#part-4-push-project-to-github)
6. [Part 5: Deploy on Render](#part-5-deploy-on-render)
7. [Part 6: Test Your Deployment](#part-6-test-your-deployment)
8. [Part 7: Troubleshooting Common Errors](#part-7-troubleshooting-common-errors)
9. [Common Beginner Mistakes](#common-beginner-mistakes)

---

## Pre-Deployment Checklist

Before starting, make sure you have:
- [ ] GitHub account (free tier: https://github.com)
- [ ] Render account (free tier: https://render.com)
- [ ] Supabase account (free tier: https://supabase.com)
- [ ] Git installed on your computer
- [ ] Your Flask app running locally without errors
- [ ] All database tables created and tested locally
- [ ] `.env` file created but NOT pushed to GitHub

---

## Part 1: Prepare Your Flask Project

### Step 1.1: Create requirements.txt

This file tells Render what Python packages to install.

```bash
# Navigate to your project root directory
cd d:\SCET\S4\DBMS\ARSHA\price-comparison-project02-main
```

**Create file: `requirements.txt`**
```
Flask==3.1.3
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
gunicorn==21.2.0
Werkzeug==3.0.1
```

**Why these packages?**
- `Flask`: Web framework
- `Flask-CORS`: Handle cross-origin requests
- `psycopg2-binary`: PostgreSQL connector
- `python-dotenv`: Load environment variables
- `gunicorn`: Production-grade server (Render uses this)
- `Werkzeug`: Security utilities for Flask

### Step 1.2: Create Procfile

This file tells Render how to start your app.

**Create file: `Procfile`** (at project root)
```
web: gunicorn app:app
```

**Explanation:**
- `web:` - This is a web process
- `gunicorn app:app` - Run gunicorn with your Flask app
  - First `app` = filename (`app.py`)
  - Second `app` = the Flask app variable inside `app.py`

### Step 1.3: Create .gitignore

This prevents sensitive files from being pushed to GitHub.

**Create file: `.gitignore`**
```
# Environment variables
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp

# Database
*.db
*.sqlite

# System
.DS_Store
Thumbs.db
```

### Step 1.4: Update app.py for Production

Your current `app.py` needs modifications for deployment.

**Replace your app.py with this:**

```python
import os
import psycopg2
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Enable CORS
CORS(app)

# ==================== DATABASE CONNECTION ====================

def get_db_connection():
    """
    Create and return a database connection
    Tries SSL first, falls back to non-SSL if needed
    """
    try:
        conn = psycopg2.connect(
            os.getenv('DATABASE_URL'),
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"SSL connection failed: {e}. Trying without SSL...")
        try:
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            return conn
        except Exception as e:
            print(f"Database connection failed: {e}")
            return None

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page with products"""
    return render_template('index.html')

@app.route('/all_products')
def all_products():
    """
    API endpoint: Return all products with prices
    Returns JSON: [{name, image_url, store_name, price, old_price, store_url}, ...]
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        
        query = """
        SELECT products.name, products.image_url, stores.store_name,
               prices.price, prices.old_price, prices.store_url
        FROM prices
        JOIN products ON prices.product_id = products.id
        JOIN stores ON prices.store_id = stores.id
        ORDER BY products.name, prices.price ASC
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        
        products_list = []
        for row in rows:
            discount = 0
            if row[4] and row[3]:  # if old_price and price exist
                discount = int(((row[4] - row[3]) / row[4]) * 100)
            
            products_list.append({
                'name': row[0],
                'image_url': row[1],
                'store_name': row[2],
                'price': float(row[3]) if row[3] else 0,
                'old_price': float(row[4]) if row[4] else 0,
                'discount_percent': discount,
                'store_url': row[5]
            })
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'products': products_list,
            'count': len(products_list)
        })
    
    except Exception as e:
        print(f"Error fetching products: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/price/<product_name>')
def get_price(product_name):
    """
    API endpoint: Search for a specific product
    Returns: Product details from all stores
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        
        query = """
        SELECT products.name, products.image_url, stores.store_name,
               prices.price, prices.old_price, prices.store_url
        FROM prices
        JOIN products ON prices.product_id = products.id
        JOIN stores ON prices.store_id = stores.id
        WHERE LOWER(products.name) LIKE LOWER(%s)
        ORDER BY prices.price ASC
        """
        
        cur.execute(query, (f'%{product_name}%',))
        rows = cur.fetchall()
        
        if not rows:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        products_list = []
        for row in rows:
            discount = 0
            if row[4] and row[3]:
                discount = int(((row[4] - row[3]) / row[4]) * 100)
            
            products_list.append({
                'name': row[0],
                'image_url': row[1],
                'store_name': row[2],
                'price': float(row[3]) if row[3] else 0,
                'old_price': float(row[4]) if row[4] else 0,
                'discount_percent': discount,
                'store_url': row[5]
            })
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'products': products_list,
            'count': len(products_list)
        })
    
    except Exception as e:
        print(f"Error searching product: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'GET':
        return render_template('user_login.html')
    
    # POST request - validate credentials
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        cur.execute('SELECT id, password FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return jsonify({'success': True, 'message': 'Login successful'})
        
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup page"""
    if request.method == 'GET':
        return render_template('signup.html')
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'User already exists'}), 400
        
        # Create new user
        hashed_password = generate_password_hash(password)
        cur.execute(
            'INSERT INTO users (username, password) VALUES (%s, %s)',
            (username, hashed_password)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Signup successful'})
    
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        cur.execute('SELECT id, password FROM admin_users WHERE username = %s', (username,))
        admin = cur.fetchone()
        cur.close()
        conn.close()
        
        if admin and check_password_hash(admin[1], password):
            session['admin_id'] = admin[0]
            session['admin_username'] = username
            return jsonify({'success': True, 'message': 'Admin login successful'})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    except Exception as e:
        print(f"Admin login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/admin_dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'admin_id' not in session:
        return render_template('admin_login.html')
    return render_template('admin_dashboard.html')

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    # Production: Use environment variable for debug mode
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    
    app.run(
        host='0.0.0.0',  # Accept connections from anywhere
        port=port,
        debug=debug_mode
    )
```

---

## Part 2: Set Up Supabase Database

### Step 2.1: Create Supabase Account and Project

1. Go to https://supabase.com
2. Click "Sign Up" → Choose GitHub (or email)
3. Authorize Supabase
4. Click "New Project"
5. Fill in:
   - **Project name**: `snap-price-comparison`
   - **Database password**: Create a strong password (save it!)
   - **Region**: Select closest to your location (e.g., `us-east-1`)
6. Click "Create new project" (wait 2-3 minutes)

### Step 2.2: Get Your Database Connection String

After project is created:
1. Go to Settings → Database
2. Look for "Connection string"
3. Choose **URI** tab (copy this!)
4. It looks like: `postgresql://postgres:password@db.supabase.co:5432/postgres`

**⚠️ SAVE THIS! You'll need it later**

### Step 2.3: Create Database Tables

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste your entire `setup.sql` file (or use this template):

```sql
-- Create stores table
CREATE TABLE IF NOT EXISTS stores (
    id SERIAL PRIMARY KEY,
    store_name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create prices table
CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    old_price DECIMAL(10, 2),
    store_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, store_id)
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create admin_users table
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create price_history table (tracks price changes)
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trigger for automatic price history
CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO price_history (product_id, store_id, price)
    VALUES (NEW.product_id, NEW.store_id, NEW.price);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER price_change_trigger
AFTER INSERT OR UPDATE ON prices
FOR EACH ROW
EXECUTE FUNCTION log_price_change();
```

4. Click **Run** (green play button)
5. You should see: ✓ Success

### Step 2.4: Insert Sample Data (Optional)

In SQL Editor, create new query:

```sql
-- Add sample stores
INSERT INTO stores (store_name) VALUES 
    ('Amazon'),
    ('Flipkart'),
    ('JioMart')
ON CONFLICT DO NOTHING;

-- Add sample products
INSERT INTO products (name, image_url) VALUES 
    ('iPhone 15', 'https://images.unsplash.com/photo-1592286927505-1def25e646e6?w=400&q=80'),
    ('Samsung Galaxy S24', 'https://images.unsplash.com/photo-1610945415295-d9bbf7ce3350?w=400&q=80')
ON CONFLICT DO NOTHING;

-- Add sample prices
INSERT INTO prices (product_id, store_id, price, old_price, store_url) 
SELECT p.id, s.id, 79999.00, 89999.00, 'https://www.amazon.com'
FROM products p, stores s 
WHERE p.name = 'iPhone 15' AND s.store_name = 'Amazon'
ON CONFLICT DO NOTHING;
```

Run it and verify ✓

---

## Part 3: Connect Flask to Supabase

### Step 3.1: Create .env File

**Create file: `.env`** (at project root)

```
# Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.iruysnusweouqqmvmwtq.supabase.co:5432/postgres

# Flask
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-to-something-random
FLASK_DEBUG=False
PORT=5000
```

**⚠️ IMPORTANT:**
- Replace `YOUR_PASSWORD` with your Supabase password
- Generate a strong `SECRET_KEY` (use: https://randomkeygen.com/)
- Never push `.env` to GitHub (add to `.gitignore`)

### Step 3.2: Test Connection Locally

Run this script to verify connection:

**Create file: `test_connection.py`**

```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM products')
    count = cur.fetchone()[0]
    print(f"✓ Connection successful!")
    print(f"✓ Found {count} products in database")
    cur.close()
    conn.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

Run it:
```bash
python test_connection.py
```

Expected output:
```
✓ Connection successful!
✓ Found X products in database
```

### Step 3.3: Test App Locally

```bash
python app.py
```

Visit http://localhost:5000 and verify it works!

---

## Part 4: Push Project to GitHub

### Step 4.1: Initialize Git Repository

```bash
# Go to project root
cd d:\SCET\S4\DBMS\ARSHA\price-comparison-project02-main

# Initialize git
git init

# Add all files
git add .

# Check what will be pushed (make sure .env is NOT listed)
git status
```

**Expected output:** You should see all files EXCEPT `.env`

### Step 4.2: First Commit

```bash
git config user.name "Your Name"
git config user.email "your.email@gmail.com"
git commit -m "Initial commit: SNAP price comparison system"
```

### Step 4.3: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `snap-price-comparison`
   - **Description**: Multi-website price comparison system with Flask
   - **Public** or **Private** (your choice)
3. Click **Create repository**
4. Copy the commands shown (they look like below)

### Step 4.4: Push to GitHub

```bash
# Add remote (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/snap-price-comparison.git

# Rename branch to main (if needed)
git branch -M main

# Push code
git push -u origin main
```

**Verify:** Go to https://github.com/USERNAME/snap-price-comparison and see your code!

---

## Part 5: Deploy on Render

### Step 5.1: Create Render Account

1. Go to https://render.com
2. Click **Sign Up**
3. Choose **GitHub** (authorize it)
4. Click **Dashboard**

### Step 5.2: Create New Web Service

1. Click **New** → **Web Service**
2. Click **Connect GitHub account** (if needed)
3. Search for your repository: `snap-price-comparison`
4. Click **Connect**

### Step 5.3: Configure Deployment Settings

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `snap-price-comparison` |
| **Environment** | `Python 3` |
| **Region** | `Ohio` (or closest to you) |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

### Step 5.4: Set Environment Variables

1. Scroll down to **Environment Variables**
2. Click **Add Environment Variable** for each:

```
DATABASE_URL = postgresql://postgres:PASSWORD@db.supabase.co:5432/postgres
FLASK_ENV = production
SECRET_KEY = your-strong-secret-key-here
FLASK_DEBUG = False
```

3. Make sure all are filled in correctly

### Step 5.5: Deploy

1. Scroll to bottom
2. Select **Free** plan (or paid if you want)
3. Click **Create Web Service**

**Wait 3-5 minutes...** You'll see deployment logs scrolling

When it says "Deploy live" ✓, your app is live!

---

## Part 6: Test Your Deployment

### Step 6.1: Get Your Render URL

After deployment, you'll see a URL like:
```
https://snap-price-comparison.onrender.com
```

### Step 6.2: Test Each Feature

**Test 1: Homepage loads**
```
https://snap-price-comparison.onrender.com/
```
Should show products (if you added sample data)

**Test 2: API endpoint works**
```
https://snap-price-comparison.onrender.com/all_products
```
Should return JSON with products

**Test 3: Search works**
```
https://snap-price-comparison.onrender.com/price/iPhone
```
Should return matching products

**Test 4: Check Logs**
In Render dashboard → Logs tab
Should show: "Listening on 0.0.0.0:10000"

### Step 6.3: Check Database Connection

Run this simple test:
```
https://snap-price-comparison.onrender.com/all_products
```

If you see products in JSON, database connection works! ✓

---

## Part 7: Troubleshooting Common Errors

### Error 1: "ModuleNotFoundError: No module named 'flask'"

**Cause:** requirements.txt not found or dependencies not installed

**Fix:**
1. Make sure `requirements.txt` is at project root
2. Check Render build logs for errors
3. Redeploy: In Render dashboard → Click "Deploy latest commit"

### Error 2: "Database connection refused"

**Cause:** DATABASE_URL is wrong or Supabase is unreachable

**Fix:**
1. Verify DATABASE_URL in Render → Environment Variables
2. Check if Supabase project is running (go to supabase.com)
3. Test locally: `python test_connection.py`

### Error 3: "SSL: CERTIFICATE_VERIFY_FAILED"

**Cause:** SSL certificate issue with Supabase

**Fix in app.py:**
```python
# Current code tries SSL then falls back
conn = psycopg2.connect(
    os.getenv('DATABASE_URL'),
    sslmode='require'  # Change to 'disable' if SSL fails
)
```

### Error 4: "Port already in use"

**Cause:** Another process using port 5000

**Fix locally:**
```bash
# On Windows
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# On Mac/Linux
lsof -i :5000
kill -9 <PID>
```

### Error 5: "No such table: products"

**Cause:** Database tables not created

**Fix:**
1. Go to Supabase → SQL Editor
2. Run your `setup.sql` file again
3. Verify tables exist in Supabase → Tables

### Error 6: "Static files not loading" (CSS/JS broken)

**Cause:** Static file paths incorrect

**Fix in app.py:**
```python
# Make sure these match your folder structure
app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)
```

### Error 7: "Build failed" on Render

**Common causes:**
- Python version mismatches (specify in `runtime.txt`)
- Missing dependencies in `requirements.txt`
- Syntax errors in `app.py`

**Fix:**
1. Check Render build logs for exact error
2. Test locally: `python app.py`
3. Check requirements.txt has all packages
4. Create `runtime.txt`:
```
python-3.11.7
```

### Error 8: "Disk usage limit exceeded"

**Cause:** Free Render plan has 0.5GB disk limit

**Fix:**
- Delete old logs: Render → Logs (scroll down, delete old entries)
- Remove large files from repository
- Upgrade to paid plan

---

## Common Beginner Mistakes

### ❌ Mistake 1: Pushing .env to GitHub

**Problem:** Your database password is now public!

**Fix:**
```bash
# Remove from Git history
git rm --cached .env
git commit -m "Remove .env file"

# Add to .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"

# Change your Supabase password immediately!
```

**Prevention:** Always add `.env` to `.gitignore` FIRST

### ❌ Mistake 2: Using localhost in production

**Problem:** `app.run(host='localhost')` won't work on Render

**Fix:**
```python
# Use 0.0.0.0 instead
app.run(host='0.0.0.0', port=5000)
```

### ❌ Mistake 3: Forgetting to update DATABASE_URL

**Problem:** App connects to local database instead of Supabase

**Fix:**
- Verify DATABASE_URL in Render Environment Variables
- Make sure it starts with `postgresql://`
- Never hardcode database credentials

### ❌ Mistake 4: Missing Procfile

**Problem:** Render doesn't know how to start your app

**Fix:**
- Create `Procfile` (no extension!)
- Content: `web: gunicorn app:app`
- Make sure `app.py` exists and `app = Flask(...)` is defined

### ❌ Mistake 5: Using SQLite in production

**Problem:** Render reset disk daily, SQLite file lost

**Fix:** Use PostgreSQL (Supabase) instead

### ❌ Mistake 6: Forgetting to commit changes

**Problem:** You updated code locally but it's not on GitHub

**Fix:**
```bash
git add .
git commit -m "Updated app with new features"
git push
# Then redeploy on Render
```

### ❌ Mistake 7: Not testing locally first

**Problem:** Broken code deployed to production

**Fix:**
```bash
# Always test locally
python app.py
# Visit http://localhost:5000
# Test all routes before pushing to GitHub
```

### ❌ Mistake 8: Using wrong SECRET_KEY

**Problem:** Sessions and security don't work

**Fix:**
```python
# Generate strong key (don't use simple strings!)
# Use: https://randomkeygen.com/
SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
```

### ❌ Mistake 9: Hardcoding API keys/passwords

**Problem:** Anyone can see your credentials

**Fix:**
```python
# ❌ WRONG
DATABASE_URL = "postgresql://postgres:password@db.com..."

# ✓ RIGHT
DATABASE_URL = os.getenv('DATABASE_URL')
```

### ❌ Mistake 10: Not handling database errors

**Problem:** App crashes with cryptic errors

**Fix:**
```python
try:
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    # ... rest of code
except Exception as e:
    print(f"Error: {e}")
    return jsonify({'error': str(e)}), 500
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
```

---

## Deployment Checklist - Final

Before deployment, verify:

- [ ] `requirements.txt` created with all packages
- [ ] `Procfile` created with `web: gunicorn app:app`
- [ ] `.gitignore` includes `.env`
- [ ] `.env` file created locally (NOT on GitHub)
- [ ] `app.py` uses environment variables
- [ ] `app.py` has error handling
- [ ] Database tables created in Supabase
- [ ] Local app runs: `python app.py`
- [ ] Code pushed to GitHub
- [ ] Render web service created
- [ ] Environment variables set in Render
- [ ] Deployment successful (check logs)
- [ ] Live URL works in browser
- [ ] API endpoints return JSON

---

## Quick Reference Commands

```bash
# Setup
git init
git config user.name "Your Name"
git config user.email "your.email@gmail.com"

# Stage and commit
git add .
git status  # Make sure .env is NOT listed!
git commit -m "Your message"

# Push to GitHub
git remote add origin https://github.com/USERNAME/snap-price-comparison.git
git push -u origin main

# Test locally
python app.py
# Visit http://localhost:5000

# Test database
python test_connection.py
pip install -r requirements.txt
```

---

## Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Supabase Documentation**: https://supabase.com/docs
- **Render Documentation**: https://render.com/docs
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Gunicorn Documentation**: https://gunicorn.org/

---

## Support & Next Steps

**After successful deployment:**

1. **Monitor your app**: Check Render logs regularly
2. **Add more products**: Insert data via Supabase SQL Editor
3. **Implement frontend auth**: Add login/signup forms
4. **Set up auto-scraping**: Use your scraper to fetch real prices
5. **Add email notifications**: Alert users on price drops
6. **Scale up**: Move to paid plans when needed

---

**Congratulations! Your app is now live on the internet! 🎉**

For questions, check the troubleshooting section or refer to official documentation links above.
