// js/pages/order-result.js

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("result-container");
    
    // Lấy orderId từ URL
    const urlParams = new URLSearchParams(window.location.search);
    const orderId = urlParams.get('orderId');

    // Lấy dữ liệu đơn hàng từ localStorage (do trang checkout lưu lại)
    const orderDataStr = localStorage.getItem("last_order");
    
    if (!orderDataStr) {
        // Trường hợp không tìm thấy dữ liệu (VD: F5 trang hoặc vào trực tiếp)
        container.innerHTML = `
            <div class="result-icon error">✕</div>
            <h2 class="text-error">Không tìm thấy thông tin đơn hàng</h2>
            <p class="muted">Đơn hàng không tồn tại hoặc đã bị xoá.</p>
            <div style="margin-top: 24px;">
                <a href="../index.html" class="btn">Về trang chủ</a>
            </div>
        `;
        return;
    }

    const order = JSON.parse(orderDataStr);

    // Kiểm tra nếu đơn hàng thành công
    if (order.status === "success") {
        renderSuccess(container, order);
    } else {
        renderError(container, order);
    }
});

function renderSuccess(container, order) {
    let html = `
        <div class="result-icon success">✓</div>
        <h2 class="text-primary" style="color: var(--color-success)">Đặt hàng thành công!</h2>
        <p class="muted">Cảm ơn bạn đã mua sắm. Mã đơn hàng của bạn là: <strong>#${order.orderId}</strong></p>
        
        <div style="background: var(--color-bg); padding: 16px; border-radius: var(--radius); margin: 24px 0; text-align: left;">
            <p style="margin: 0 0 8px 0;"><strong>Phương thức thanh toán:</strong> ${order.paymentMethod === 'cod' ? 'Thanh toán khi nhận hàng (COD)' : 'Chuyển khoản ngân hàng'}</p>
            <p style="margin: 0;"><strong>Hình thức nhận:</strong> ${order.shippingMethod === 'delivery' ? 'Giao hàng tận nơi' : 'Nhận tại cửa hàng'}</p>
        </div>
    `;

    // Nếu chọn chuyển khoản, hiển thị thêm nút sang trang QR
    if (order.paymentMethod === 'bank') {
        html += `
            <div class="status status-loading" style="text-align: left; margin-bottom: 24px;">
                <strong>Lưu ý:</strong> Vui lòng quét mã QR để hoàn tất thanh toán. Đơn hàng sẽ được xử lý sau khi nhận được tiền.
            </div>
            <div style="display: flex; gap: 12px; justify-content: center;">
                <a href="payment-qr.html?orderId=${order.orderId}" class="btn btn-primary">Thanh toán ngay (QR)</a>
                <a href="items.html" class="btn">Tiếp tục mua sắm</a>
            </div>
        `;
    } else {
        // Nếu là COD
        html += `
            <div style="margin-top: 24px;">
                <a href="items.html" class="btn btn-primary">Tiếp tục mua sắm</a>
            </div>
        `;
    }

    container.innerHTML = html;
}

function renderError(container, order) {
    container.innerHTML = `
        <div class="result-icon error">✕</div>
        <h2 class="text-error">Đặt hàng thất bại</h2>
        <p class="muted">Rất tiếc, đã có lỗi xảy ra trong quá trình xử lý đơn hàng.</p>
        <div class="status status-error" style="text-align: left;">
            <strong>Lý do:</strong> Hệ thống thanh toán từ chối giao dịch hoặc sản phẩm đã hết hàng.
        </div>
        <div style="margin-top: 24px; display: flex; gap: 12px; justify-content: center;">
            <a href="checkout.html" class="btn btn-primary">Thử lại</a>
            <a href="items.html" class="btn">Về giỏ hàng</a>
        </div>
    `;
}