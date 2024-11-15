# createtable.py

import sqlite3
import os

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Connect to SQLite database
conn = sqlite3.connect('data/shopping.db')
cursor = conn.cursor()

# Products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id TEXT,
    inventory INTEGER DEFAULT 0
)
''')

# Users table with authentication and preferences
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
)
''')

# User sessions
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Shopping cart
cursor.execute('''
CREATE TABLE IF NOT EXISTS cart_items (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    price_at_time DECIMAL(10,2) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
)
''')

# Orders
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status TEXT CHECK(status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Order items
cursor.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price_at_time DECIMAL(10,2) NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
)
''')

# Product categories
cursor.execute('''
CREATE TABLE IF NOT EXISTS product_categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    parent_id INTEGER,
    FOREIGN KEY(parent_id) REFERENCES product_categories(id)
)
''')


# Product Categories
cursor.execute('''
INSERT INTO product_categories (id, name, description, parent_id) VALUES
('CAT001', 'Electronics', 'Electronic devices and accessories', NULL),
('CAT002', 'Computers', 'Computers and accessories', 'CAT001'),
('CAT003', 'Audio', 'Audio equipment', 'CAT001'),
('CAT004', 'Clothing', 'Apparel and fashion', NULL),
('CAT005', 'Shoes', 'Footwear', 'CAT004')
''')

# Products
cursor.execute('''

INSERT INTO products (id, name, description, price, category_id, inventory) VALUES 
-- Audio (CAT003)
('PROD001', 'Sony WH-1000XM4', 'Wireless noise-cancelling headphones', 349.99, 'CAT003', 100),
('PROD004', 'Apple AirPods Pro', 'Wireless earbuds with active noise cancellation', 249.99, 'CAT003', 150),
('PROD005', 'Bose QuietComfort 35', 'Premium wireless headphones', 299.99, 'CAT003', 75),
('PROD006', 'JBL Flip 6', 'Portable Bluetooth speaker', 129.99, 'CAT003', 200),

-- Computers (CAT002)
('PROD002', 'MacBook Pro 14"', 'Apple M1 Pro laptop', 1999.99, 'CAT002', 20),
('PROD007', 'Dell XPS 13', 'Ultra-thin Windows laptop', 1299.99, 'CAT002', 30),
('PROD008', 'HP Pavilion Desktop', 'Home office desktop computer', 799.99, 'CAT002', 25),
('PROD009', 'Lenovo ThinkPad X1', 'Business laptop', 1499.99, 'CAT002', 15),

-- General Electronics (CAT001)
('PROD010', 'iPad Air', '10.9-inch Apple tablet', 599.99, 'CAT001', 80),
('PROD011', 'Samsung 4K TV', '55-inch Smart LED TV', 699.99, 'CAT001', 40),
('PROD012', 'Canon EOS R6', 'Mirrorless digital camera', 2499.99, 'CAT001', 10),
('PROD013', 'Nintendo Switch', 'Gaming console', 299.99, 'CAT001', 60),

-- Clothing (CAT004)
('PROD014', 'Levi''s 501 Jeans', 'Classic fit denim jeans', 69.99, 'CAT004', 200),
('PROD015', 'North Face Jacket', 'Waterproof hiking jacket', 199.99, 'CAT004', 45),
('PROD016', 'Ralph Lauren Polo', 'Classic cotton polo shirt', 89.99, 'CAT004', 150),
('PROD017', 'Calvin Klein T-Shirt', 'Basic crew neck tee', 29.99, 'CAT004', 300),

-- Shoes (CAT005)
('PROD003', 'Nike Air Max', 'Running shoes', 129.99, 'CAT005', 50),
('PROD018', 'Adidas Ultra Boost', 'Performance running shoes', 179.99, 'CAT005', 40),
('PROD019', 'Converse Chuck Taylor', 'Classic canvas sneakers', 59.99, 'CAT005', 150),
('PROD020', 'Vans Old Skool', 'Skateboarding shoes', 69.99, 'CAT005', 100)
''')

# Users
cursor.execute('''
INSERT INTO users (id, name, email) VALUES
('USER001', 'John Doe', 'john@example.com'),
('USER002', 'Jane Smith', 'jane@example.com')   
''')

cursor.execute('''
-- Insert orders for USER001
INSERT INTO orders (id, user_id, total_amount, status, created_at) VALUES
('ORD001', 'USER001', 349.99, 'delivered', '2024-02-01 10:00:00'),
('ORD002', 'USER001', 499.98, 'shipped', '2024-02-15 14:30:00'),
('ORD003', 'USER001', 129.99, 'confirmed', '2024-03-01 09:15:00'),
('ORD004', 'USER001', 1999.99, 'delivered', '2024-03-05 16:45:00'),
('ORD005', 'USER001', 299.99, 'pending', '2024-03-10 11:20:00');

''')

cursor.execute('''
-- Insert order items
INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES
('ORD001', 'PROD001', 1, 349.99),  -- Sony WH-1000XM4
('ORD002', 'PROD004', 2, 249.99),  -- AirPods Pro
('ORD003', 'PROD006', 1, 129.99),  -- JBL Flip 6
('ORD004', 'PROD002', 1, 1999.99), -- MacBook Pro
('ORD005', 'PROD003', 1, 299.99);  -- Nike Air Max
''')


# Commit changes and close connection
conn.commit()
conn.close()