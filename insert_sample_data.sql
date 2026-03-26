-- Add sample stores
INSERT INTO stores (store_name) VALUES 
    ('Amazon'),
    ('Flipkart'),
    ('JioMart')
ON CONFLICT DO NOTHING;

-- Add sample products
INSERT INTO products (name, image_url) VALUES 
    ('iPhone 15', 'https://images.unsplash.com/photo-1592286927505-1def25e646e6?w=400&q=80'),
    ('Samsung Galaxy S24', 'https://images.unsplash.com/photo-1610945415295-d9bbf7ce3350?w=400&q=80'),
    ('MacBook Pro 16', 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80'),
    ('iPad Air', 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&q=80'),
    ('AirPods Pro 2', 'https://images.unsplash.com/photo-1606841837239-c5a1a3a07af7?w=400&q=80')
ON CONFLICT DO NOTHING;

-- Add sample prices
INSERT INTO prices (product_id, store_id, price, old_price, store_url) 
SELECT p.id, s.id, 79999.00, 89999.00, 'https://www.amazon.com'
FROM products p, stores s 
WHERE p.name = 'iPhone 15' AND s.store_name = 'Amazon'
ON CONFLICT DO NOTHING;

INSERT INTO prices (product_id, store_id, price, old_price, store_url) 
SELECT p.id, s.id, 82000.00, 89999.00, 'https://www.flipkart.com'
FROM products p, stores s 
WHERE p.name = 'iPhone 15' AND s.store_name = 'Flipkart'
ON CONFLICT DO NOTHING;

INSERT INTO prices (product_id, store_id, price, old_price, store_url) 
SELECT p.id, s.id, 81500.00, 89999.00, 'https://www.jiomart.com'
FROM products p, stores s 
WHERE p.name = 'iPhone 15' AND s.store_name = 'JioMart'
ON CONFLICT DO NOTHING;

INSERT INTO prices (product_id, store_id, price, old_price, store_url) 
SELECT p.id, s.id, 69999.00, 79999.00, 'https://www.amazon.com'
FROM products p, stores s 
WHERE p.name = 'Samsung Galaxy S24' AND s.store_name = 'Amazon'
ON CONFLICT DO NOTHING;

INSERT INTO prices (product_id, store_id, price, old_price, store_url) 
SELECT p.id, s.id, 71999.00, 79999.00, 'https://www.flipkart.com'
FROM products p, stores s 
WHERE p.name = 'Samsung Galaxy S24' AND s.store_name = 'Flipkart'
ON CONFLICT DO NOTHING;

INSERT INTO prices (product_id, store_id, price, old_price, store_url) 
SELECT p.id, s.id, 199999.00, 229999.00, 'https://www.amazon.com'
FROM products p, stores s 
WHERE p.name = 'MacBook Pro 16' AND s.store_name = 'Amazon'
ON CONFLICT DO NOTHING;

INSERT INTO prices (product_id, store_id, price, old_price, store_url) 
SELECT p.id, s.id, 201999.00, 229999.00, 'https://www.jiomart.com'
FROM products p, stores s 
WHERE p.name = 'MacBook Pro 16' AND s.store_name = 'JioMart'
ON CONFLICT DO NOTHING;

INSERT INTO prices (product_id, store_id, price, old_price, store_url) 
SELECT p.id, s.id, 54999.00, 64999.00, 'https://www.flipkart.com'
FROM products p, stores s 
WHERE p.name = 'iPad Air' AND s.store_name = 'Flipkart'
ON CONFLICT DO NOTHING;

INSERT INTO prices (product_id, store_id, price, old_price, store_url) 
SELECT p.id, s.id, 27999.00, 29999.00, 'https://www.amazon.com'
FROM products p, stores s 
WHERE p.name = 'AirPods Pro 2' AND s.store_name = 'Amazon'
ON CONFLICT DO NOTHING;
