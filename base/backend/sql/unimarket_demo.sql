DROP DATABASE IF EXISTS unimarket;
CREATE DATABASE unimarket
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE unimarket;

CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(100) NOT NULL UNIQUE,
    email       VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


CREATE TABLE items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    description TEXT NULL,
    price       DECIMAL(12,2) NOT NULL DEFAULT 0,
    stock       INT NOT NULL DEFAULT 0,
    is_active   TINYINT(1) NOT NULL DEFAULT 1,
    is_sold     TINYINT(1) NOT NULL DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- 3. CARTS  (khớp app/models/cart.py)
--    Cart: id, user_id (unique, FK users), created_at, updated_at
-- ---------------------------------------------------------
CREATE TABLE carts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL UNIQUE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_carts_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- 4. CART_ITEMS  (khớp app/models/cart_item.py)
--    CartItem: id, cart_id, product_id, quantity
--    UNIQUE(cart_id, product_id)
-- ---------------------------------------------------------
CREATE TABLE cart_items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    cart_id     INT NOT NULL,
    product_id  INT NOT NULL,
    quantity    INT NOT NULL DEFAULT 1,

    CONSTRAINT uq_cart_product UNIQUE (cart_id, product_id),

    CONSTRAINT fk_cart_items_cart
        FOREIGN KEY (cart_id) REFERENCES carts(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_cart_items_product
        FOREIGN KEY (product_id) REFERENCES items(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE orders (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    user_id           INT NOT NULL,
    recipient         VARCHAR(100) NOT NULL,
    address           VARCHAR(255) NOT NULL,
    receiving_method  ENUM('DELIVERY', 'PICKUP') NOT NULL,
    payment_method    ENUM('COD', 'BANK_TRANSFER', 'E_WALLET') NOT NULL,
    total_amount      DECIMAL(12,2) NOT NULL DEFAULT 0,
    status            ENUM(
                          'PENDING',
                          'CONFIRMED',
                          'SHIPPING',
                          'COMPLETED',
                          'CANCELLED'
                      ) NOT NULL DEFAULT 'PENDING',
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_orders_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE order_items (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL,
    product_id      INT NULL,
    product_name    VARCHAR(255) NOT NULL,
    price_at_order  DECIMAL(12,2) NOT NULL,
    quantity        INT NOT NULL,
    subtotal        DECIMAL(12,2) NOT NULL,

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id) REFERENCES orders(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id) REFERENCES items(id)
        ON DELETE SET NULL
) ENGINE=InnoDB;


INSERT INTO users (username, email, password) VALUES
('nguyenvana', 'vana@gmail.com', 'demo123'),
('tranthib',  'thib@gmail.com',  'demo123');

-- Items (bảng tên items, không phải products)
INSERT INTO items (name, price, stock, description) VALUES
('Áo thun Unimarket', 150000, 50, 'Áo thun cotton'),
('Quần Jean',         350000, 30, 'Quần jean nam'),
('Giày Sneaker',      650000, 20, 'Giày thể thao'),
('Balo Laptop',       450000, 15, 'Balo đựng laptop');

-- Cart của user 1
INSERT INTO carts (user_id) VALUES (1);

-- 2 sản phẩm trong giỏ
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES
(1, 1, 2),
(1, 2, 1);

-- 1 đơn hàng mẫu
INSERT INTO orders (
    user_id, recipient, address,
    receiving_method, payment_method,
    total_amount, status
) VALUES (
    1, 'Nguyen Van A', 'Ha Noi, Viet Nam',
    'DELIVERY', 'COD',
    650000, 'PENDING'
);

-- Chi tiết đơn hàng
INSERT INTO order_items (
    order_id, product_id, product_name,
    price_at_order, quantity, subtotal
) VALUES
(1, 1, 'Áo thun Unimarket', 150000, 2, 300000),
(1, 2, 'Quần Jean',         350000, 1, 350000);