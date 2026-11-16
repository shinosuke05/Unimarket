-- Tạo database app_db + bảng categories, items.
-- Cách chạy bằng MySQL Workbench:
--   File > Open SQL Script... > chọn file này > bấm nút tia sét (Execute) > Refresh ô SCHEMAS.
-- Bảng users sẽ được tạo tự động khi chạy server hoặc chạy: python -m app.db.seed_admin

SET NAMES utf8mb4; -- để tiếng Việt không bị lỗi font

CREATE DATABASE IF NOT EXISTS app_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE app_db;

CREATE TABLE IF NOT EXISTS categories (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(100) NOT NULL UNIQUE,
  description TEXT NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
  updated_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX ix_items_category_id (category_id),
  INDEX ix_items_deleted_at (deleted_at),
  CONSTRAINT fk_items_category FOREIGN KEY (category_id)
    REFERENCES categories(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO items (name, description, price) VALUES
  ('Cơm rang dưa bò', 'Món mẫu để kiểm tra API', 45000),
  ('Trà đá', 'Dữ liệu mẫu số 2', 5000);
