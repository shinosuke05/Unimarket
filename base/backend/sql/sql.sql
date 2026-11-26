-- =========================================================
-- Unimarket - schema tham khảo
-- Backend tự tạo bảng và thêm cột khi khởi động (xem app/db/schema_sync.py).
-- File này dùng để tạo database thủ công hoặc đối chiếu cấu trúc.
-- An toàn khi chạy lại: không xoá dữ liệu.
-- =========================================================

CREATE DATABASE IF NOT EXISTS app_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE app_db;

CREATE TABLE IF NOT EXISTS users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  full_name     VARCHAR(100) NOT NULL,
  email         VARCHAR(255) NOT NULL UNIQUE,
  phone         VARCHAR(20) NULL,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('CUSTOMER','ADMIN') NOT NULL,
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS addresses (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT NOT NULL,
  recipient_name  VARCHAR(100) NOT NULL,
  phone           VARCHAR(20) NOT NULL,
  street_address  VARCHAR(255) NOT NULL,
  is_default      TINYINT(1) NOT NULL DEFAULT 0,
  INDEX ix_addresses_user_id (user_id),
  CONSTRAINT fk_addresses_user FOREIGN KEY (user_id)
    REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categories (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(100) NOT NULL UNIQUE,
  description TEXT NULL,
  is_active   TINYINT(1) NOT NULL DEFAULT 1,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS items (
  id                 INT AUTO_INCREMENT PRIMARY KEY,
  name               VARCHAR(255) NOT NULL,
  description        TEXT NULL,
  price              DECIMAL(12,2) NOT NULL DEFAULT 0,
  quantity           INT NOT NULL DEFAULT 1,
  item_condition     ENUM('NEW','LIKE_NEW','GOOD','FAIR') NOT NULL DEFAULT 'GOOD',
  status             ENUM('AVAILABLE','SOLD','HIDDEN') NOT NULL DEFAULT 'AVAILABLE',
  category_id        INT NULL,
  legacy_product_id  INT NULL,
  condition_percent  VARCHAR(30) NULL,
  deleted_at         DATETIME NULL,
  created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX ix_items_category_id (category_id),
  INDEX ix_items_deleted_at (deleted_at),
  CONSTRAINT fk_items_category FOREIGN KEY (category_id)
    REFERENCES categories(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS item_images (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  item_id     INT NOT NULL,
  url         VARCHAR(500) NOT NULL,
  is_primary  TINYINT(1) NOT NULL DEFAULT 0,
  sort_order  INT NOT NULL DEFAULT 0,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_item_images_item_id (item_id),
  CONSTRAINT fk_item_images_item FOREIGN KEY (item_id)
    REFERENCES items(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS carts (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL UNIQUE,
  created_at  DATETIME NULL,
  updated_at  DATETIME NULL,
  CONSTRAINT fk_carts_user FOREIGN KEY (user_id)
    REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cart_items (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  cart_id     INT NOT NULL,
  product_id  INT NOT NULL,
  quantity    INT NOT NULL DEFAULT 1,
  UNIQUE KEY uq_cart_product (cart_id, product_id),
  CONSTRAINT fk_cart_items_cart FOREIGN KEY (cart_id)
    REFERENCES carts(id) ON DELETE CASCADE,
  CONSTRAINT fk_cart_items_item FOREIGN KEY (product_id)
    REFERENCES items(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS orders (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  user_id           INT NOT NULL,
  recipient         VARCHAR(100) NOT NULL,
  address           VARCHAR(255) NOT NULL,
  receiver_phone    VARCHAR(20) NULL,
  receiving_method  ENUM('DELIVERY','PICKUP') NOT NULL,
  payment_method    ENUM('COD','BANK_TRANSFER','E_WALLET') NOT NULL,
  subtotal          DECIMAL(12,2) NOT NULL DEFAULT 0,
  shipping_fee      DECIMAL(12,2) NOT NULL DEFAULT 0,
  total_amount      DECIMAL(12,2) NOT NULL DEFAULT 0,
  note              VARCHAR(500) NULL,
  status            ENUM('PENDING','CONFIRMED','SHIPPING','COMPLETED','CANCELLED')
                    NOT NULL DEFAULT 'PENDING',
  created_at        DATETIME NULL,
  INDEX ix_orders_user_id (user_id),
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id)
    REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_items (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  order_id        INT NOT NULL,
  product_id      INT NULL,
  product_name    VARCHAR(255) NOT NULL,
  price_at_order  DECIMAL(12,2) NOT NULL,
  quantity        INT NOT NULL,
  subtotal        DECIMAL(12,2) NOT NULL,
  INDEX ix_order_items_order_id (order_id),
  CONSTRAINT fk_order_items_order FOREIGN KEY (order_id)
    REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_order_items_item FOREIGN KEY (product_id)
    REFERENCES items(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_status_histories (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  order_id    INT NULL,
  old_status  VARCHAR(50) NULL,
  new_status  VARCHAR(50) NULL,
  note        TEXT NULL,
  changed_by  INT NULL,
  created_at  DATETIME NULL,
  INDEX ix_order_status_histories_order_id (order_id),
  CONSTRAINT fk_order_history_order FOREIGN KEY (order_id)
    REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_order_history_changed_by FOREIGN KEY (changed_by)
    REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS payments (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  order_id          INT NOT NULL UNIQUE,
  method            VARCHAR(50) NULL,
  amount            DECIMAL(12,2) NULL,
  status            VARCHAR(30) NULL,
  transaction_code  VARCHAR(100) NULL,
  transfer_note     VARCHAR(255) NULL,
  proof_image_url   VARCHAR(500) NULL,
  confirmed_by      INT NULL,
  paid_at           DATETIME NULL,
  created_at        DATETIME NULL,
  updated_at        DATETIME NULL,
  CONSTRAINT fk_payments_order FOREIGN KEY (order_id)
    REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_payments_confirmed_by FOREIGN KEY (confirmed_by)
    REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS store_settings (
  id                    INT AUTO_INCREMENT PRIMARY KEY,
  qr_code               VARCHAR(255) NULL,
  bank_name             VARCHAR(100) NULL,
  bank_account          VARCHAR(50) NULL,
  bank_owner            VARCHAR(100) NULL,
  phone                 VARCHAR(20) NULL,
  zalo                  VARCHAR(255) NULL,
  facebook              VARCHAR(255) NULL,
  updated_at            DATETIME NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  category_id     INT NOT NULL,
  name            VARCHAR(255) NOT NULL,
  description     TEXT NULL,
  price           DECIMAL(12,2) NOT NULL,
  item_condition  VARCHAR(30) NOT NULL,
  stock           INT NOT NULL DEFAULT 1,
  status          VARCHAR(20) NOT NULL DEFAULT 'available',
  is_visible      TINYINT(1) NOT NULL DEFAULT 1,
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX ix_products_category_id (category_id),
  INDEX ix_products_status_created_at (status, created_at),
  INDEX ix_products_price (price),
  CONSTRAINT fk_products_category FOREIGN KEY (category_id)
    REFERENCES categories(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS product_images (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  product_id  INT NOT NULL,
  image_url   VARCHAR(500) NOT NULL,
  is_primary  TINYINT(1) NOT NULL DEFAULT 0,
  sort_order  INT NOT NULL DEFAULT 0,
  INDEX ix_product_images_product_id (product_id),
  CONSTRAINT fk_product_images_product FOREIGN KEY (product_id)
    REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;
