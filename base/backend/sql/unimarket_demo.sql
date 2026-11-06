CREATE DATABASE IF NOT EXISTS unimarket
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE unimarket;

-- 1. Bảng Users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- 2. Bảng Products
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    description TEXT
);

-- 3. Bảng Carts
CREATE TABLE carts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 4. Bảng Cart Items
CREATE TABLE cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,

    UNIQUE KEY uq_cart_product (cart_id, product_id),

    FOREIGN KEY (cart_id) REFERENCES carts(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 5. Bảng Orders
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    recipient VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    receiving_method ENUM('DELIVERY', 'PICKUP') NOT NULL,
    payment_method ENUM(
        'COD',
        'BANK_TRANSFER',
        'E_WALLET'
    ) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    status ENUM(
        'PENDING',
        'CONFIRMED',
        'SHIPPING',
        'COMPLETED',
        'CANCELLED'
    ) NOT NULL DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 6. Bảng Order Items
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NULL,
    product_name VARCHAR(255) NOT NULL,
    price_at_order DECIMAL(12,2) NOT NULL,
    quantity INT NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,

    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE SET NULL
);

-- 7. Dữ liệu Users
INSERT INTO users (username, email, password) VALUES
('nguyenvana', 'vana@gmail.com', 'demo123'),
('tranthib', 'thib@gmail.com', 'demo123');

-- 8. Dữ liệu Products
INSERT INTO products (name, price, stock, description) VALUES
('Áo thun Unimarket', 150000, 50, 'Áo thun cotton'),
('Quần Jean', 350000, 30, 'Quần jean nam'),
('Giày Sneaker', 650000, 20, 'Giày thể thao'),
('Balo Laptop', 450000, 15, 'Balo đựng laptop');

-- 9. Dữ liệu Cart
INSERT INTO carts (user_id) VALUES (1);

-- 10. Dữ liệu Cart Items
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES
(1, 1, 2),
(1, 2, 1);

-- 11. Dữ liệu Orders
INSERT INTO orders (
    user_id,
    recipient,
    address,
    receiving_method,
    payment_method,
    total_amount,
    status
) VALUES (
    1,
    'Nguyen Van A',
    'Ha Noi, Viet Nam',
    'DELIVERY',
    'COD',
    650000,
    'PENDING'
);

-- 12. Dữ liệu Order Items
INSERT INTO order_items (
    order_id,
    product_id,
    product_name,
    price_at_order,
    quantity,
    subtotal
) VALUES
(1, 1, 'Áo thun Unimarket', 150000, 2, 300000),
(1, 2, 'Quần Jean', 350000, 1, 350000);

-- Kiểm tra dữ liệu
SELECT * FROM users;
SELECT * FROM products;
SELECT * FROM carts;
SELECT * FROM cart_items;
SELECT * FROM orders;
SELECT * FROM order_items;
