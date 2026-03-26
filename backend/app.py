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
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)
app.secret_key = "mysecretkey"

CORS(app)

# Database connection with conditional SSL
db_url = os.environ.get('DATABASE_URL')
try:
    # Try with SSL (for Supabase)
    conn = psycopg2.connect(
        db_url,
        sslmode='require',
        connect_timeout=5
    )
except Exception as e:
    # Fall back to no SSL (for localhost)
    print(f"SSL connection failed, trying without SSL: {e}")
    try:
        conn = psycopg2.connect(db_url)
    except Exception as e2:
        print(f"Connection failed: {e2}")
        raise

cur = conn.cursor()


# ================= SERVE CLONES =================
@app.route('/clones/<path:filename>')
def serve_clones(filename):
    clones_path = os.path.join(os.path.dirname(__file__), '../clones')
    return send_from_directory(clones_path, filename)


# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html", username=session.get("username"))


# ================= GET PRODUCT (SEARCH) =================
@app.route("/price/<product>")
def get_price(product):
    try:
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
        conn.rollback()
        return jsonify({"error": str(e)})


# ================= ALL PRODUCTS (HOMEPAGE) =================
@app.route("/all_products")
def all_products():
    try:
        query = """
        SELECT products.name, products.image_url, stores.store_name,
               prices.price, prices.original_price, prices.discount_percent,
               prices.is_on_sale, prices.store_url
        FROM prices
        JOIN products ON prices.product_id = products.id
        JOIN stores ON prices.store_id = stores.id
        ORDER BY products.name, prices.price ASC
        """

        cur.execute(query)
        data = cur.fetchall()

        result = []
        for row in data:
            result.append({
                "product": row[0],
                "image": row[1],
                "store": row[2],
                "price": float(row[3]),
                "original_price": float(row[4]) if row[4] else None,
                "discount_percent": row[5],
                "is_on_sale": row[6],
                "store_url": row[7]
            })

        return jsonify(result)

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)})


# ================= USER LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def user_login():

    if request.method == "POST":
        try:
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
            conn.rollback()
            return f"Login error: {str(e)}"

    return render_template("user_login.html")


# ================= SIGNUP =================
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        try:
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
            conn.rollback()
            return f"Signup error: {str(e)}"

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

    try:
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
        conn.rollback()
        return f"Admin login error: {str(e)}"


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
            MIN(discount_percent) as min_discount,
            ROUND(SUM(pr.original_price - pr.price)::numeric, 0) as total_savings
        FROM prices pr
        WHERE pr.is_on_sale = TRUE
        """
        
        cur.execute(query)
        row = cur.fetchone()
        
        stats = {
            "total_products_on_sale": row[0],
            "average_discount_percent": float(row[1]) if row[1] else 0,
            "max_discount_percent": row[2],
            "min_discount_percent": row[3],
            "total_customer_savings": float(row[4]) if row[4] else 0
        }
        
        return jsonify(stats)
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)})


# ================= BEST DEALS ENDPOINT =================
@app.route("/best_deals")
def best_deals():
    """Get top deals sorted by discount percentage and savings"""
    try:
        query = """
        SELECT p.name, s.store_name, pr.price, pr.original_price,
               pr.discount_percent,
               (pr.original_price - pr.price) as savings
        FROM prices pr
        JOIN products p ON pr.product_id = p.id
        JOIN stores s ON pr.store_id = s.id
        WHERE pr.is_on_sale = TRUE
        ORDER BY pr.discount_percent DESC, savings DESC
        LIMIT 5
        """
        
        cur.execute(query)
        data = cur.fetchall()
        
        result = []
        for row in data:
            result.append({
                "product": row[0],
                "store": row[1],
                "sale_price": float(row[2]),
                "original_price": float(row[3]) if row[3] else None,
                "discount_percent": row[4],
                "savings": float(row[5]) if row[5] else 0,
                "badge": f"{row[4]}% OFF 🔥"
            })
        
        return jsonify({
            "best_deals": result,
            "message": f"Found {len(result)} amazing deals!"
        })
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)})


# ================= SALES DASHBOARD =================
@app.route("/sales_dashboard")
def sales_dashboard():
    """Render beautiful sales dashboard with all data"""
    try:
        # Get best deals (same as /best_deals API)
        best_deals_query = """
        SELECT p.name, s.store_name, pr.price, pr.original_price,
               pr.discount_percent,
               (pr.original_price - pr.price) as savings
        FROM prices pr
        JOIN products p ON pr.product_id = p.id
        JOIN stores s ON pr.store_id = s.id
        WHERE pr.is_on_sale = TRUE
        ORDER BY pr.discount_percent DESC, savings DESC
        LIMIT 5
        """
        
        cur.execute(best_deals_query)
        deals_data = cur.fetchall()
        best_deals = []
        for row in deals_data:
            best_deals.append({
                "product": row[0],
                "store": row[1],
                "sale_price": float(row[2]),
                "original_price": float(row[3]) if row[3] else None,
                "discount_percent": row[4],
                "savings": float(row[5]) if row[5] else 0
            })
        
        # Get all on-sale products
        all_sales_query = """
        SELECT p.name, s.store_name, pr.price, pr.original_price,
               pr.discount_percent,
               (pr.original_price - pr.price) as savings
        FROM prices pr
        JOIN products p ON pr.product_id = p.id
        JOIN stores s ON pr.store_id = s.id
        WHERE pr.is_on_sale = TRUE
        ORDER BY pr.discount_percent DESC, savings DESC
        """
        
        cur.execute(all_sales_query)
        all_sales_data = cur.fetchall()
        all_on_sale = []
        for row in all_sales_data:
            all_on_sale.append({
                "name": row[0],
                "store_name": row[1],
                "price": float(row[2]),
                "original_price": float(row[3]) if row[3] else None,
                "discount_percent": row[4],
                "savings": float(row[5]) if row[5] else 0
            })
        
        # Get statistics
        stats_query = """
        SELECT 
            COUNT(DISTINCT pr.id) as total_on_sale,
            ROUND(AVG(pr.discount_percent)::numeric, 2) as avg_discount,
            MAX(pr.discount_percent) as max_discount,
            MIN(pr.discount_percent) as min_discount,
            SUM(pr.original_price - pr.price) as total_savings
        FROM prices pr
        WHERE pr.is_on_sale = TRUE
        """
        
        cur.execute(stats_query)
        stats_row = cur.fetchone()
        stats = {
            "total_products_on_sale": stats_row[0] or 0,
            "average_discount_percent": float(stats_row[1]) if stats_row[1] else 0,
            "max_discount_percent": int(stats_row[2]) if stats_row[2] else 0,
            "min_discount_percent": int(stats_row[3]) if stats_row[3] else 0,
            "total_customer_savings": float(stats_row[4]) if stats_row[4] else 0
        }
        
        return render_template(
            "sales_dashboard.html",
            best_deals=best_deals,
            all_on_sale=all_on_sale,
            stats=stats
        )
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)})


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)