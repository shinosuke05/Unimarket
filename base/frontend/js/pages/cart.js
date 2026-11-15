// js/pages/cart.js

// Lấy dữ liệu giỏ hàng từ localStorage
function getCart() {
    const cart = localStorage.getItem("cart");
    return cart ? JSON.parse(cart) : [];
}

// Lưu giỏ hàng vào localStorage
function saveCart(cart) {
    localStorage.setItem("cart", JSON.stringify(cart));
    // Cập nhật lại số lượng trên header ngay lập tức
    if (window.updateCartBadge) window.updateCartBadge();
}

// Render giao diện giỏ hàng
function renderCart() {
    const cart = getCart();
    const tbody = document.getElementById("cart-table-body");
    const emptyMsg = document.getElementById("cart-empty");
    const cartContent = document.getElementById("cart-content");
    const grandTotalEl = document.getElementById("cart-grand-total");

    if (cart.length === 0) {
        emptyMsg.style.display = "block";
        cartContent.style.display = "none";
        return;
    }

    emptyMsg.style.display = "none";
    cartContent.style.display = "block";

    let grandTotal = 0;

    tbody.innerHTML = cart.map((item, index) => {
        const itemTotal = item.price * item.quantity;
        grandTotal += itemTotal;

        return `
      <tr>
        <td>
          <strong>${escapeHtml(item.name)}</strong>
          <div class="muted" style="font-size: 12px;">Mã SP: #${item.id}</div>
        </td>
        <td class="text-right">${formatMoney(item.price)}</td>
        <td>
          <div class="qty-control">
            <button class="btn btn-small" onclick="changeQty(${index}, -1)">-</button>
            <span class="qty-value">${item.quantity}</span>
            <button class="btn btn-small" onclick="changeQty(${index}, 1)">+</button>
          </div>
        </td>
        <td class="text-right"><strong>${formatMoney(itemTotal)}</strong></td>
        <td class="actions">
          <button class="btn btn-small btn-danger" onclick="removeFromCart(${index}, '${escapeHtml(item.name)}')">Xoá</button>
        </td>
      </tr>
    `;
    }).join("");

    grandTotalEl.textContent = formatMoney(grandTotal);
}

// Hàm thay đổi số lượng (truyền vào vị trí index và số lượng thay đổi: 1 hoặc -1)
window.changeQty = function (index, delta) {
    const cart = getCart();
    if (!cart[index]) return;

    cart[index].quantity += delta;

    // Nếu số lượng giảm về 0 hoặc nhỏ hơn, hỏi có muốn xoá không
    if (cart[index].quantity <= 0) {
        if (confirm(`Bạn có muốn xoá "${cart[index].name}" khỏi giỏ hàng?`)) {
            cart.splice(index, 1);
            showToast("Đã xoá sản phẩm khỏi giỏ");
        } else {
            cart[index].quantity = 1; // Khôi phục lại 1 nếu không xoá
        }
    }

    saveCart(cart);
    renderCart();
};

// Hàm xoá sản phẩm có xác nhận
window.removeFromCart = function (index, name) {
    if (confirm(`Bạn có chắc chắn muốn xoá "${name}" khỏi giỏ hàng?`)) {
        const cart = getCart();
        cart.splice(index, 1);
        saveCart(cart);
        renderCart();
        showToast("Đã xoá sản phẩm khỏi giỏ");
    }
};

// Khởi chạy khi tải trang
document.addEventListener("DOMContentLoaded", () => {
    renderCart();
});