from flask import Flask, jsonify, render_template, request, redirect, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

# Initialize Flask
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)
app.secret_key = "mysecretkey"

CORS(app)

# Database connection
conn = psycopg2.connect(
    database="price_comparison",
    user="postgres",
    password="root123",
    host="localhost",
    port="5432"
)
cur = conn.cursor()


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
                "SELECT * FROM users WHERE username=%s",
                (username,)
            )

            user = cur.fetchone()

            if user and check_password_hash(user[2], password):
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
            "SELECT * FROM admin_users WHERE username=%s",
            (username,)
        )

        admin = cur.fetchone()

        if admin and check_password_hash(admin[2], password):
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


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)