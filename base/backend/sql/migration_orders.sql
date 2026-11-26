-- File: backend/sql/migration_orders.sql  (thư mục: backend/sql/)
-- Chạy 1 lần trên DB đã có sẵn (create_all không sửa bảng cũ).
ALTER TABLE items ADD COLUMN stock INT NOT NULL DEFAULT 1;

-- Sau đó chạy lại uvicorn: create_all tạo lại orders, order_items, order_status_history, payments, store_settings.

-- Dữ liệu mẫu để test (thay 1 bằng id user / item thật):
-- UPDATE items SET stock = 10 WHERE id = 1;
-- INSERT INTO orders (buyer_id, receiver_name, receiver_phone, shipping_address, total_amount, status)
--   VALUES (1, 'Nguyễn Văn A', '0912345678', 'KTX Khu B, ĐHQG', 90000, 'PENDING');
-- INSERT INTO order_items (order_id, item_id, item_name, price, quantity)
--   VALUES (LAST_INSERT_ID(), 1, 'Giáo trình Giải tích 1', 45000, 2);
-- UPDATE items SET stock = stock - 2 WHERE id = 1;