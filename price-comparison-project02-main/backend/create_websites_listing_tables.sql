-- Create websites table to store site information
CREATE TABLE IF NOT EXISTS websites (
    site_id SERIAL PRIMARY KEY,
    site_name VARCHAR(255) NOT NULL UNIQUE,
    site_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create listing table to store product listings from websites
CREATE TABLE IF NOT EXISTS listing (
    listing_id SERIAL PRIMARY KEY,
    site_id INT NOT NULL REFERENCES websites(site_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    product_url TEXT NOT NULL,
    current_price DECIMAL(10, 2),
    availability_status VARCHAR(50) DEFAULT 'In Stock',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, site_id)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_listing_site_id ON listing(site_id);
CREATE INDEX IF NOT EXISTS idx_listing_product_id ON listing(product_id);
CREATE INDEX IF NOT EXISTS idx_listing_availability ON listing(availability_status);

-- Insert sample website data
INSERT INTO websites (site_name, site_url) VALUES 
    ('Amazon', 'https://www.amazon.com'),
    ('Flipkart', 'https://www.flipkart.com'),
    ('JioMart', 'https://www.jiomart.com')
ON CONFLICT (site_name) DO NOTHING;

-- Display confirmation
SELECT 'websites table created successfully' AS status;
SELECT 'listing table created successfully' AS status;
SELECT COUNT(*) as total_websites FROM websites;
