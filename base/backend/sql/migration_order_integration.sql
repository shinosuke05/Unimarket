
USE app_db;

-- 1. Bo sung thong tin don hang
ALTER TABLE orders
    ADD COLUMN receiver_phone VARCHAR(20) NULL,
    ADD COLUMN subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN shipping_fee DECIMAL(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN note VARCHAR(500) NULL;

-- 2. Bo sung thong tin thanh toan
ALTER TABLE payments
    ADD COLUMN transfer_note VARCHAR(255) NULL,
    ADD COLUMN proof_image_url VARCHAR(500) NULL,
    ADD COLUMN confirmed_by INT NULL,
    ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    ADD CONSTRAINT fk_payments_confirmed_by
        FOREIGN KEY (confirmed_by) REFERENCES users(id);

-- 3. Bo sung nguoi thay doi trang thai don hang
ALTER TABLE order_status_histories
    ADD COLUMN changed_by INT NULL,
    ADD CONSTRAINT fk_order_history_changed_by
        FOREIGN KEY (changed_by) REFERENCES users(id);

-- 4. Moi don hang co toi da mot ban ghi thanh toan
ALTER TABLE payments
    MODIFY COLUMN order_id INT NOT NULL,
    ADD CONSTRAINT uq_payments_order_id UNIQUE (order_id);
