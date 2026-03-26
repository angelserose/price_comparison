-- Remove sample products and their associated prices
DELETE FROM prices WHERE product_id IN (
    SELECT id FROM products 
    WHERE name IN ('iPhone 15', 'Samsung Galaxy S24', 'MacBook Pro 16', 'iPad Air', 'AirPods Pro 2')
);

DELETE FROM products 
WHERE name IN ('iPhone 15', 'Samsung Galaxy S24', 'MacBook Pro 16', 'iPad Air', 'AirPods Pro 2');

-- Verify removal
SELECT COUNT(*) as remaining_products FROM products;
SELECT COUNT(*) as remaining_prices FROM prices;
