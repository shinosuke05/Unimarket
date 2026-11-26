
"use strict";

let cartItems = [];
let cartBusy = false;

async function loadCart() {
    const empty = document.getElementById("cart-empty");
    const content = document.getElementById("cart-content");

    content.style.display = "none";
    empty.style.display = "block";

    if (!localStorage.getItem("token")) {
        empty.textContent = "Bạn cần đăng nhập để xem giỏ hàng.";

        const link = document.createElement("a");
        link.href = "auth.html";
        link.textContent = " Đăng nhập";
        empty.appendChild(link);
        return;
    }

    empty.textContent = "Đang tải giỏ hàng...";

    try {
        const result = await api.get("/cart");
        renderCart(result);
    } catch (error) {
        empty.textContent =
            error.message || "Không thể tải giỏ hàng.";
    }
}

function renderCart(result) {
    cartItems = result.items || [];

    const tbody = document.getElementById("cart-table-body");
    const empty = document.getElementById("cart-empty");
    const content = document.getElementById("cart-content");
    const total = document.getElementById("cart-grand-total");

    tbody.replaceChildren();

    if (!cartItems.length) {
        empty.style.display = "block";
        content.style.display = "none";

        empty.textContent = "Giỏ hàng đang trống.";

        const link = document.createElement("a");
        link.href = "products.html";
        link.textContent = " Tiếp tục mua sắm";
        empty.appendChild(link);

        return;
    }

    empty.style.display = "none";
    content.style.display = "block";

    tbody.innerHTML = cartItems.map(item => `
        <tr>
            <td>
                <strong>${escapeHtml(item.product_name)}</strong>
                <div class="muted">
                    Mã SP: #${Number(item.product_id)}
                </div>
            </td>

            <td class="text-right">
                ${formatMoney(Number(item.price))}
            </td>

            <td>
                <div class="qty-control">
                    <button class="btn btn-small"
                        onclick="changeQty(${Number(item.id)}, -1)">
                        -
                    </button>

                    <span class="qty-value">
                        ${Number(item.quantity)}
                    </span>

                    <button class="btn btn-small"
                        onclick="changeQty(${Number(item.id)}, 1)">
                        +
                    </button>
                </div>
            </td>

            <td class="text-right">
                <strong>
                    ${formatMoney(Number(item.subtotal))}
                </strong>
            </td>

            <td class="actions">
                <button class="btn btn-small btn-danger"
                    onclick="removeFromCart(${Number(item.id)})">
                    Xóa
                </button>
            </td>
        </tr>
    `).join("");

    total.textContent = formatMoney(
        Number(result.total_amount)
    );
}

window.changeQty = async function (id, delta) {
    if (cartBusy) return;

    const item = cartItems.find(
        row => Number(row.id) === id
    );

    if (!item) return;

    const quantity = Number(item.quantity) + delta;

    if (quantity < 1) {
        return window.removeFromCart(id);
    }

    cartBusy = true;

    try {
        const result = await api.put(
            `/cart/items/${id}`,
            { quantity }
        );

        renderCart(result);

        if (window.updateCartBadge) {
            window.updateCartBadge();
        }

    } catch (error) {
        showToast(error.message, "error");
    } finally {
        cartBusy = false;
    }
};

window.removeFromCart = async function (id) {
    if (cartBusy) return;

    const item = cartItems.find(
        row => Number(row.id) === id
    );

    if (!item) return;

    if (!confirm(
        `Bạn có muốn xóa "${item.product_name}" khỏi giỏ hàng?`
    )) return;

    cartBusy = true;

    try {
        const result = await api.delete(
            `/cart/items/${id}`
        );

        renderCart(result);

        if (window.updateCartBadge) {
            window.updateCartBadge();
        }

        showToast("Đã xóa sản phẩm khỏi giỏ hàng");

    } catch (error) {
        showToast(error.message, "error");
    } finally {
        cartBusy = false;
    }
};

document.addEventListener("DOMContentLoaded", loadCart);
