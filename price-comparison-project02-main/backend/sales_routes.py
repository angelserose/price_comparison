# Add these routes to your existing app.py

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
            savings = float(row[2]) - float(row[3]) if row[3] else 0
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
