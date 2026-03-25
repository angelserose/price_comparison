import psycopg2
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()
# Connect database
conn = psycopg2.connect(
    os.environ.get('DATABASE_URL'),
    sslmode='require'
)

cur = conn.cursor()

stores = [
    ("../clones/amazon/index.html", 1, "/clones/amazon/index.html"),
    ("../clones/flipkart/index.html", 2, "/clones/flipkart/index.html"),
    ("../clones/jiomart/index.html", 3, "/clones/jiomart/index.html")
]

for file_path, store_id, store_base_url in stores:

    print("\nScraping store:", store_id)

    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    if store_id == 3:
        products = soup.find_all("div", class_="product-card")
        name_tag = "h3"
        price_tag = "p"
        price_class = "price"
    else:
        products = soup.find_all("div", class_="product")
        name_tag = "h2"
        price_tag = "span"
        price_class = "price"

    for item in products:

        name = item.find(name_tag, class_="product-name" if store_id != 3 else None).text.strip()
        price_text = item.find(price_tag, class_=price_class).text.strip()
        if store_id == 3:
            price_text = price_text.replace("₹", "")
        price = float(price_text)

        # 🔥 GET IMAGE
        image_tag = item.find("img")
        image = image_tag["src"] if image_tag else ""

        # 🔥 CREATE STORE URL (add product name as query parameter)
        store_url = f"{store_base_url}?product={name.replace(' ', '+')}"

        # Check if product exists
        cur.execute(
            "SELECT id FROM products WHERE LOWER(name)=LOWER(%s)",
            (name,)
        )

        product = cur.fetchone()

        if product:
            product_id = product[0]

            # 🔥 UPDATE IMAGE (IMPORTANT)
            cur.execute(
                "UPDATE products SET image_url=%s WHERE id=%s",
                (image, product_id)
            )

        else:
            # Insert new product
            cur.execute(
                "INSERT INTO products (name, image_url) VALUES (%s, %s) RETURNING id",
                (name, image)
            )
            product_id = cur.fetchone()[0]
            print("Inserted new product:", name)

        # Insert / update price with store_url
        cur.execute(
            """
            INSERT INTO prices (product_id, store_id, price, store_url)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (product_id,store_id)
            DO UPDATE SET price = EXCLUDED.price, store_url = EXCLUDED.store_url;
            """,
            (product_id, store_id, price, store_url)
        )

        print("Updated price for:", name, price)

conn.commit()
cur.close()
conn.close()