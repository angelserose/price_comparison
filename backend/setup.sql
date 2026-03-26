-- Connect to price_comparison

CREATE TABLE IF NOT EXISTS stores (
    id SERIAL PRIMARY KEY,
    store_name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image_url TEXT
);

CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    store_id INT REFERENCES stores(id),
    price DECIMAL(10,2),
    old_price DECIMAL(10,2),
    store_url TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Insert stores
INSERT INTO stores (store_name) VALUES ('Amazon'), ('Flipkart'), ('JioMart') ON CONFLICT DO NOTHING;

-- Insert default users
INSERT INTO users (username, password) VALUES ('user', 'user123') ON CONFLICT DO NOTHING;
INSERT INTO admin_users (username, password) VALUES ('admin', 'admin123') ON CONFLICT DO NOTHING;