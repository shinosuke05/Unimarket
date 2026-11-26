
-- Thực hiện một lần trên database đã backup.

USE app_db;

-- Bổ sung thông tin liên kết với sản phẩm cũ
-- và tình trạng sản phẩm theo phần trăm.

ALTER TABLE items
    ADD COLUMN legacy_product_id INT NULL,
    ADD COLUMN condition_percent VARCHAR(30) NULL,
    ADD CONSTRAINT uq_items_legacy_product
        UNIQUE (legacy_product_id);

START TRANSACTION;

-- Chuyển sản phẩm sang bảng items.
INSERT INTO items (
    name,
    description,
    price,
    quantity,
    item_condition,
    status,
    category_id,
    deleted_at,
    created_at,
    updated_at,
    legacy_product_id,
    condition_percent
)
SELECT
    p.name,
    p.description,
    p.price,
    p.stock,

    CASE
        WHEN CAST(
            REPLACE(p.item_condition, '%', '')
            AS UNSIGNED
        ) = 100 THEN 'NEW'

        WHEN CAST(
            REPLACE(p.item_condition, '%', '')
            AS UNSIGNED
        ) >= 90 THEN 'LIKE_NEW'

        WHEN CAST(
            REPLACE(p.item_condition, '%', '')
            AS UNSIGNED
        ) >= 70 THEN 'GOOD'

        ELSE 'FAIR'
    END,

    CASE
        WHEN p.is_visible = 0 THEN 'HIDDEN'
        WHEN p.stock <= 0 THEN 'SOLD'
        WHEN LOWER(p.status) = 'sold' THEN 'SOLD'
        ELSE 'AVAILABLE'
    END,

    p.category_id,
    NULL,
    p.created_at,
    p.updated_at,
    p.id,
    p.item_condition

FROM products p
WHERE NOT EXISTS (
    SELECT 1
    FROM items i
    WHERE i.legacy_product_id = p.id
);

-- Chuyển ảnh theo ID sản phẩm mới.
INSERT INTO item_images (
    item_id,
    url,
    is_primary,
    sort_order
)
SELECT
    i.id,
    pi.image_url,
    pi.is_primary,
    pi.sort_order
FROM product_images pi
JOIN items i
    ON i.legacy_product_id = pi.product_id
WHERE NOT EXISTS (
    SELECT 1
    FROM item_images ii
    WHERE ii.item_id = i.id
      AND ii.url = pi.image_url
      AND ii.sort_order = pi.sort_order
);

COMMIT;
