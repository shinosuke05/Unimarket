-- Tạo lại database app_db từ đầu.
-- CẢNH BÁO: xoá toàn bộ dữ liệu trong app_db (kể cả tài khoản).
CREATE DATABASE IF NOT EXISTS app_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE app_db;

CREATE TABLE categories (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(100) NOT NULL UNIQUE,
  description TEXT NULL,
  is_active   TINYINT(1) NOT NULL DEFAULT 1,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE items (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO items (name, description, price) VALUES
  ('Cơm rang dưa bò', 'Món mẫu để kiểm tra API', 45000),
  ('Trà đá', 'Dữ liệu mẫu số 2', 5000);