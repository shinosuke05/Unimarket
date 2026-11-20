// js/pages/checkout.js

document.addEventListener("DOMContentLoaded", () => {
    renderSummary();

    // Lắng nghe sự kiện submit form
    document.getElementById("checkout-form").addEventListener("submit", handleCheckout);
});

// Hàm lấy giỏ hàng
function getCart() {
    return JSON.parse(localStorage.getItem("cart") || "[]");
}

// Tính toán và hiển thị tóm tắt đơn hàng
function renderSummary() {
    const cart = getCart();
    const summaryContainer = document.getElementById("checkout-summary-items");

    if (cart.length === 0) {
        summaryContainer.innerHTML = `<p class="muted">Giỏ hàng trống. <a href="items.html">Quay lại mua sắm</a></p>`;
        return;
    }

    let subtotal = 0;
    let html = cart.map(item => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;
        return `
            <div class="summary-item">
                <span>${escapeHtml(item.name)} <strong style="color:var(--color-muted)">x${item.quantity}</strong></span>
                <span>${formatMoney(itemTotal)}</span>
            </div>
        `;
    }).join("");

    // Phí ship mặc định (Giao hàng tận nơi)
    const shippingFee = 30000; 
    
    html += `
        <div class="summary-item" style="margin-top: 16px; border-top: 1px dashed var(--color-border); padding-top: 16px;">
            <span>Tạm tính</span>
            <span>${formatMoney(subtotal)}</span>
        </div>
        <div class="summary-item">
            <span>Phí vận chuyển</span>
            <span>${formatMoney(shippingFee)}</span>
        </div>
        <div class="summary-total">
            <span>Tổng cộng</span>
            <span class="text-primary">${formatMoney(subtotal + shippingFee)}</span>
        </div>
    `;

    summaryContainer.innerHTML = html;
}

// Xử lý khi bấm nút "Xác nhận Đặt hàng"
async function handleCheckout(event) {
    event.preventDefault();
    
    const addressId = document.getElementById("address-select").value;
    if (!addressId) {
        showToast("Vui lòng chọn địa chỉ nhận hàng!", "error");
        return;
    }

    const paymentMethod = document.querySelector('input[name="payment"]:checked').value;
    const shippingMethod = document.querySelector('input[name="shipping"]:checked').value;
    const cart = getCart();

    if (cart.length === 0) {
        showToast("Giỏ hàng trống, không thể đặt hàng!", "error");
        return;
    }

    // Giả lập gọi API tạo đơn hàng (Bạn có thể thay bằng api.post('/orders', data) sau này)
    const btnSubmit = event.target.querySelector('button[type="submit"]');
    btnSubmit.disabled = true;
    btnSubmit.textContent = "Đang xử lý...";

    try {
        // Giả lập độ trễ mạng 1 giây
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Tạo mã đơn hàng giả lập
        const orderId = "ORD" + Math.floor(Math.random() * 1000000);
        const orderData = {
            orderId: orderId,
            addressId,
            shippingMethod,
            paymentMethod,
            items: cart,
            status: "success" // Giả lập luôn thành công
        };

        // Lưu trạng thái đơn hàng vào localStorage để trang kết quả đọc
        localStorage.setItem("last_order", JSON.stringify(orderData));
        
        // Xoá giỏ hàng sau khi đặt thành công
        localStorage.removeItem("cart");
        if (window.updateCartBadge) window.updateCartBadge();

        // Điều hướng sang trang kết quả
        window.location.href = `order-result.html?orderId=${orderId}`;

    } catch (error) {
        showToast("Có lỗi xảy ra khi đặt hàng. Vui lòng thử lại.", "error");
        btnSubmit.disabled = false;
        btnSubmit.textContent = "Xác nhận Đặt hàng";
    }
}