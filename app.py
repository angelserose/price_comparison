from flask import Flask, jsonify, render_template, request, redirect, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

CORS(app)

# ================= DATABASE CONNECTION FUNCTION =================
def get_db_connection():
    """Create database connection on-demand"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL not set!")
        return None
    
    try:
        # Try with SSL (for Supabase)
        conn = psycopg2.connect(db_url, sslmode='require', connect_timeout=5)
        return conn
    except Exception as e:
        # Fall back to no SSL (for localhost)
        try:
            conn = psycopg2.connect(db_url)
            return conn
        except Exception as e2:
            print(f"Database connection error: {e2}")
            return None


# ================= SERVE CLONES =================
@app.route('/clones/<path:filename>')
def serve_clones(filename):
    clones_path = os.path.join(os.path.dirname(__file__), 'clones')
    return send_from_directory(clones_path, filename)


# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html", username=session.get("username"))


# ================= GET PRODUCT (SEARCH) =================
@app.route("/price/<product>")
def get_price(product):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cur = conn.cursor()
        
        query = """
        SELECT products.name, products.image_url, stores.store_name,
               prices.price, prices.old_price, prices.store_url
        FROM prices
        JOIN products ON prices.product_id = products.id
        JOIN stores ON prices.store_id = stores.id
        WHERE products.name ILIKE %s
        ORDER BY prices.price ASC
        """

        cur.execute(query, (f"%{product}%",))
        data = cur.fetchall()

        result = []
        for row in data:
            result.append({
                "product": row[0],
                "image": row[1],
                "store": row[2],
                "price": float(row[3]),
                "old_price": float(row[4]) if row[4] else 0,
                "store_url": row[5]
            })

        return jsonify(result)

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# ================= ALL PRODUCTS (HOMEPAGE) =================
@app.route("/all_products")
def all_products():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
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
        data = cur.fetchall()

        result = []
        for row in data:
            # Calculate discount if old_price exists
            discount = 0
            if row[4] and row[3]:
                discount = int(((row[4] - row[3]) / row[4]) * 100)
            
            result.append({
                "product": row[0],
                "image": row[1],
                "store": row[2],
                "price": float(row[3]),
                "old_price": float(row[4]) if row[4] else None,
                "discount_percent": discount,
                "is_on_sale": True if discount > 0 else False,
                "store_url": row[5]
            })

        return jsonify(result)

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# ================= USER LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def user_login():

    if request.method == "POST":
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            if not conn:
                return "Database connection failed", 500
            
            cur = conn.cursor()
            
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            
            if not username or not password:
                return "Please enter both username and password"

            cur.execute(
                "SELECT id, username, password FROM users WHERE username=%s",
                (username,)
            )

            user = cur.fetchone()

            if user:
                # user[2] is the password
                stored_pass = user[2].strip() if user[2] else ""
                
                # Try both plain and hashed password checks
                if stored_pass == password or (stored_pass.startswith("scrypt:") and check_password_hash(stored_pass, password)):
                    session["username"] = username
                    return redirect("/")

            return "Invalid login credentials"

        except Exception as e:
            if conn:
                conn.rollback()
            return f"Login error: {str(e)}", 500
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template("user_login.html")


# ================= SIGNUP =================
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            if not conn:
                return "Database connection failed", 500
            
            cur = conn.cursor()
            
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            
            if not username or not password:
                return "Please enter both username and password"
            
            if len(password) < 6:
                return "Password must be at least 6 characters"

            # Check existing user
            cur.execute(
                "SELECT * FROM users WHERE username=%s",
                (username,)
            )

            if cur.fetchone():
                return "User already exists. Try different username."

            # Hash password and insert user
            hashed_password = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )

            conn.commit()
            return redirect("/login")

        except Exception as e:
            if conn:
                conn.rollback()
            return f"Signup error: {str(e)}", 500
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template("signup.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("admin", None)
    return redirect("/")


# ================= ADMIN LOGIN =================
@app.route("/admin", methods=["GET"])
def admin_page():
    return render_template("admin_login.html")


@app.route("/admin/login", methods=["POST"])
def admin_login():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if not conn:
            return "Database connection failed", 500
        
        cur = conn.cursor()
        
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            return "Please enter both username and password"

        cur.execute(
            "SELECT id, username, password FROM admin_users WHERE username=%s",
            (username,)
        )

        admin = cur.fetchone()

        if admin:
            # admin[2] is the password
            stored_pass = admin[2].strip() if admin[2] else ""
            
            # Try both plain and hashed password checks
            if stored_pass == password or (stored_pass.startswith("scrypt:") and check_password_hash(stored_pass, password)):
                session["admin"] = username
                return redirect("/admin/dashboard")

        return "Invalid admin credentials"
    
    except Exception as e:
        if conn:
            conn.rollback()
        return f"Admin login error: {str(e)}", 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# ================= ADMIN DASHBOARD =================
@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    try:
        cur.execute("""
            SELECT products.id, products.name, stores.id, stores.store_name, prices.price
            FROM prices
            JOIN products ON prices.product_id = products.id
            JOIN stores ON prices.store_id = stores.id
            ORDER BY products.id
        """)

        data = cur.fetchall()
        return render_template("admin_dashboard.html", data=data)
    
    except Exception as e:
        conn.rollback()
        return f"Dashboard error: {str(e)}"


# ================= UPDATE PRICE =================
@app.route("/update_price", methods=["POST"])
def update_price():

    try:
        product_id = request.form.get("product_id", "").strip()
        store_id = request.form.get("store_id", "").strip()
        price = request.form.get("price", "").strip()
        
        if not product_id or not store_id or not price:
            return redirect("/admin/dashboard")
        
        price = float(price)
        
        cur.execute(
            "UPDATE prices SET price=%s WHERE product_id=%s AND store_id=%s",
            (price, product_id, store_id)
        )

        conn.commit()
        return redirect("/admin/dashboard")
    
    except Exception as e:
        conn.rollback()
        return f"Update error: {str(e)}"


# ================= GET SALE PRODUCTS =================
@app.route("/on_sale")
def on_sale_products():
    """Get all products currently on sale"""
    try:
        query = """
        SELECT p.name, s.store_name, 
               pr.price, pr.original_price, pr.discount_percent
        FROM prices pr
        JOIN products p ON pr.product_id = p.id
        JOIN stores s ON pr.store_id = s.id
        WHERE pr.is_on_sale = TRUE
        ORDER BY pr.discount_percent DESC, pr.price ASC
        """
        
        cur.execute(query)
        data = cur.fetchall()
        
        result = []
        for row in data:
            savings = float(row[3]) - float(row[2]) if row[3] else 0
            result.append({
                "product": row[0],
                "store": row[1],
                "sale_price": float(row[2]),
                "original_price": float(row[3]) if row[3] else None,
                "discount_percent": row[4],
                "savings": savings
            })
        
        return jsonify(result)
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)})


# ================= GET CHEAPEST VERSION OF PRODUCT =================
@app.route("/cheapest/<product>")
def cheapest_deal(product):
    """Get the cheapest version of a product across all stores"""
    try:
        query = """
        SELECT p.name, s.store_name, pr.price, pr.original_price, 
               pr.discount_percent, pr.is_on_sale
        FROM prices pr
        JOIN products p ON pr.product_id = p.id
        JOIN stores s ON pr.store_id = s.id
        WHERE p.name ILIKE %s
        ORDER BY pr.price ASC
        """
        
        cur.execute(query, (f"%{product}%",))
        data = cur.fetchall()
        
        if not data:
            return jsonify({"message": "Product not found"}), 404
        
        # First one is cheapest
        cheapest = data[0]
        
        result = {
            "product": cheapest[0],
            "cheapest_store": cheapest[1],
            "price": float(cheapest[2]),
            "original_price": float(cheapest[3]) if cheapest[3] else None,
            "discount_percent": cheapest[4],
            "on_sale": cheapest[5],
            "all_options": []
        }
        
        # Add all options
        for row in data:
            result["all_options"].append({
                "store": row[1],
                "price": float(row[2]),
                "original_price": float(row[3]) if row[3] else None,
                "discount_percent": row[4],
                "on_sale": row[5]
            })
        
        return jsonify(result)
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)})


# ================= SALE STATISTICS =================
@app.route("/sale_stats")
def sale_stats():
    """Get sale statistics and trending discounts"""
    try:
        query = """
        SELECT 
            COUNT(*) as total_on_sale,
            ROUND(AVG(discount_percent)::numeric, 1) as avg_discount,
            MAX(discount_percent) as max_discount,
            MIN(price) as min_price,
            MAX(price) as max_price
        FROM prices
        WHERE is_on_sale = TRUE
        """
        
        cur.execute(query)
        data = cur.fetchone()
        
        if data:
            result = {
                "total_on_sale": data[0],
                "average_discount": float(data[1]) if data[1] else 0,
                "max_discount": float(data[2]) if data[2] else 0,
                "min_price": float(data[3]) if data[3] else 0,
                "max_price": float(data[4]) if data[4] else 0
            }
        else:
            result = {
                "total_on_sale": 0,
                "average_discount": 0,
                "max_discount": 0,
                "min_price": 0,
                "max_price": 0
            }
        
        return jsonify(result)
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)})


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
