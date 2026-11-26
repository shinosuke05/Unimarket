-- Bổ sung cấu trúc bảng items cho module quản lý sản phẩm.
-- Chạy một lần trên database cũ đã kiểm tra.

ALTER TABLE items
    ADD COLUMN quantity INT NOT NULL DEFAULT 1,
    ADD COLUMN item_condition
        ENUM('NEW', 'LIKE_NEW', 'GOOD', 'FAIR')
        NOT NULL DEFAULT 'GOOD',
    ADD COLUMN status
        ENUM('AVAILABLE', 'SOLD', 'HIDDEN')
        NOT NULL DEFAULT 'AVAILABLE',
    ADD COLUMN category_id INT NULL,
    ADD COLUMN deleted_at DATETIME NULL,
    ADD INDEX ix_items_category_id (category_id),
    ADD INDEX ix_items_deleted_at (deleted_at),
    ADD CONSTRAINT fk_items_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE RESTRICT;