-- ============================================================
-- UNIMARKET - SCHEMA HỢP NHẤT (dùng init.sql làm chuẩn)
-- Chạy 1 lần: File > Open SQL Script > Execute
-- ============================================================

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS app_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE app_db;

-- ------------------------------------------------------------
-- 1. USERS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  username    VARCHAR(100) NOT NULL UNIQUE,
  email       VARCHAR(255) NOT NULL UNIQUE,
  password    VARCHAR(255) NOT NULL,
  role        ENUM('USER','ADMIN') NOT NULL DEFAULT 'USER',
  is_active   BOOLEAN NOT NULL DEFAULT TRUE,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 2. CATEGORIES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(100) NOT NULL UNIQUE,
  description TEXT NULL,
  is_active   BOOLEAN NOT NULL DEFAULT TRUE,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 3. ITEMS  (schema chuẩn từ init.sql gốc)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS items (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  name           VARCHAR(255) NOT NULL,
  description    TEXT NULL,
  price          DECIMAL(12, 2) NOT NULL DEFAULT 0,
  quantity       INT NOT NULL DEFAULT 1,
  item_condition ENUM('NEW','LIKE_NEW','GOOD','FAIR') NOT NULL DEFAULT 'GOOD',
  status         ENUM('AVAILABLE','SOLD','HIDDEN') NOT NULL DEFAULT 'AVAILABLE',
  category_id    INT NULL,
  deleted_at     DATETIME NULL,
  created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                 ON UPDATE CURRENT_TIMESTAMP,
  INDEX ix_items_category_id (category_id),
  INDEX ix_items_deleted_at (deleted_at),
  CONSTRAINT fk_items_category FOREIGN KEY (category_id)
    REFERENCES categories(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 4. ITEM_IMAGES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS item_images (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  item_id     INT NOT NULL,
  url         VARCHAR(500) NOT NULL,
  is_primary  BOOLEAN NOT NULL DEFAULT FALSE,
  sort_order  INT NOT NULL DEFAULT 0,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_item_images_item_id (item_id),
  CONSTRAINT fk_item_images_item FOREIGN KEY (item_id)
    REFERENCES items(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 5. CARTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS carts (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL UNIQUE,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
              ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_carts_user FOREIGN KEY (user_id)
    REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 6. CART_ITEMS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cart_items (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  cart_id     INT NOT NULL,
  item_id     INT NOT NULL,
  quantity    INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_cart_item UNIQUE (cart_id, item_id),
  CONSTRAINT fk_cart_items_cart FOREIGN KEY (cart_id)
    REFERENCES carts(id) ON DELETE CASCADE,
  CONSTRAINT fk_cart_items_item FOREIGN KEY (item_id)
    REFERENCES items(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 7. ORDERS  (gộp cột từ migration_order_integration.sql)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  buyer_id          INT NOT NULL,
  receiver_name     VARCHAR(100) NOT NULL,
  receiver_phone    VARCHAR(20) NULL,
  shipping_address  VARCHAR(255) NOT NULL,
  note              VARCHAR(500) NULL,
  receiving_method  ENUM('DELIVERY','PICKUP') NOT NULL DEFAULT 'DELIVERY',
  payment_method    ENUM('COD','BANK_TRANSFER','E_WALLET') NOT NULL DEFAULT 'COD',
  subtotal          DECIMAL(12,2) NOT NULL DEFAULT 0,
  shipping_fee      DECIMAL(12,2) NOT NULL DEFAULT 0,
  total_amount      DECIMAL(12,2) NOT NULL DEFAULT 0,
  status            ENUM('PENDING','CONFIRMED','SHIPPING','COMPLETED','CANCELLED')
                    NOT NULL DEFAULT 'PENDING',
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
  INDEX ix_orders_buyer_id (buyer_id),
  INDEX ix_orders_status (status),
  CONSTRAINT fk_orders_buyer FOREIGN KEY (buyer_id)
    REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 8. ORDER_ITEMS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  order_id        INT NOT NULL,
  item_id         INT NULL,
  item_name       VARCHAR(255) NOT NULL,
  price_at_order  DECIMAL(12,2) NOT NULL,
  quantity        INT NOT NULL,
  subtotal        DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_order_items_order FOREIGN KEY (order_id)
    REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_order_items_item FOREIGN KEY (item_id)
    REFERENCES items(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 9. PAYMENTS  (gộp cột từ migration_order_integration.sql)
--    1 đơn hàng ↔ tối đa 1 payment
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  order_id         INT NOT NULL,
  amount           DECIMAL(12,2) NOT NULL DEFAULT 0,
  method           ENUM('COD','BANK_TRANSFER','E_WALLET') NOT NULL DEFAULT 'COD',
  status           ENUM('PENDING','PAID','FAILED','REFUNDED')
                   NOT NULL DEFAULT 'PENDING',
  transfer_note    VARCHAR(255) NULL,
  proof_image_url  VARCHAR(500) NULL,
  confirmed_by     INT NULL,
  created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                   ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT uq_payments_order_id UNIQUE (order_id),
  CONSTRAINT fk_payments_order FOREIGN KEY (order_id)
    REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_payments_confirmed_by FOREIGN KEY (confirmed_by)
    REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 10. ORDER_STATUS_HISTORIES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_status_histories (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  order_id    INT NOT NULL,
  old_status  VARCHAR(20) NULL,
  new_status  VARCHAR(20) NOT NULL,
  note        VARCHAR(500) NULL,
  changed_by  INT NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_osh_order_id (order_id),
  CONSTRAINT fk_osh_order FOREIGN KEY (order_id)
    REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_osh_changed_by FOREIGN KEY (changed_by)
    REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 11. STORE_SETTINGS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS store_settings (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  key_name      VARCHAR(100) NOT NULL UNIQUE,
  value         TEXT NULL,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SEED DATA
-- ============================================================

INSERT IGNORE INTO users (username, email, password, role) VALUES
  ('admin',      'admin@unimarket.local', 'admin123', 'ADMIN'),
  ('nguyenvana', 'vana@gmail.com',        'demo123',  'USER'),
  ('tranthib',   'thib@gmail.com',        'demo123',  'USER');

INSERT IGNORE INTO categories (name, description) VALUES
  ('Đồ ăn',      'Món ăn, đồ uống'),
  ('Đồ điện tử', 'Thiết bị điện tử'),
  ('Sách',       'Giáo trình, sách tham khảo');

INSERT IGNORE INTO items (name, description, price, quantity, item_condition, status, category_id) VALUES
  ('Cơm rang dưa bò', 'Món mẫu để kiểm tra API', 45000, 10, 'GOOD', 'AVAILABLE', 1),
  ('Trà đá',          'Dữ liệu mẫu số 2',         5000, 100, 'GOOD', 'AVAILABLE', 1),
  ('Giáo trình Giải tích 1', 'Sách đại học',      45000, 5,  'LIKE_NEW', 'AVAILABLE', 3);

INSERT IGNORE INTO carts (user_id) VALUES (2);

INSERT IGNORE INTO cart_items (cart_id, item_id, quantity) VALUES
  (1, 1, 2),
  (1, 2, 1);

INSERT IGNORE INTO orders (
  buyer_id, receiver_name, receiver_phone, shipping_address,
  receiving_method, payment_method, subtotal, shipping_fee,
  total_amount, status
) VALUES (
  2, 'Nguyễn Văn A', '0912345678', 'KTX Khu B, ĐHQG',
  'DELIVERY', 'COD', 95000, 15000, 110000, 'PENDING'
);

INSERT IGNORE INTO order_items (
  order_id, item_id, item_name, price_at_order, quantity, subtotal
) VALUES
  (1, 1, 'Cơm rang dưa bò', 45000, 2, 90000),
  (1, 2, 'Trà đá',          5000,  1, 5000);

INSERT IGNORE INTO payments (order_id, amount, method, status) VALUES
  (1, 110000, 'COD', 'PENDING');

INSERT IGNORE INTO store_settings (key_name, value) VALUES
  ('store_name',    'UniMarket'),
  ('store_phone',   '0900000000'),
  ('store_address', 'ĐHQG TP.HCM');