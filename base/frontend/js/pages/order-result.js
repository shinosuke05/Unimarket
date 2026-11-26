
"use strict";

const ORDER_STATUS_LABELS = {
    PENDING: "Chờ xác nhận",
    CONFIRMED: "Đã xác nhận",
    SHIPPING: "Đang giao hàng",
    COMPLETED: "Đã hoàn thành",
    CANCELLED: "Đã hủy"
};

const PAYMENT_LABELS = {
    COD: "Thanh toán khi nhận hàng (COD)",
    BANK_TRANSFER: "Chuyển khoản ngân hàng",
    E_WALLET: "Ví điện tử"
};

const SHIPPING_LABELS = {
    DELIVERY: "Giao hàng tận nơi",
    PICKUP: "Nhận tại cửa hàng"
};

async function loadOrderResult() {
    const container = document.getElementById(
        "result-container"
    );

    if (!localStorage.getItem("token")) {
        window.location.href = "auth.html";
        return;
    }

    const params = new URLSearchParams(
        window.location.search
    );

    const orderId = Number(params.get("orderId"));

    if (
        !Number.isSafeInteger(orderId) ||
        orderId < 1
    ) {
        renderError(
            container,
            "Mã đơn hàng không hợp lệ."
        );
        return;
    }

    container.innerHTML = `
        <div class="status status-loading">
            Đang tải thông tin đơn hàng...
        </div>
    `;

    try {
        const order = await api.get(
            `/orders/${orderId}`
        );

        renderOrder(container, order);

        if (window.updateCartBadge) {
            window.updateCartBadge();
        }

    } catch (error) {
        renderError(
            container,
            error.message ||
            "Không thể tải thông tin đơn hàng."
        );
    }
}

function renderOrder(container, order) {
    const cancelled =
        order.status === "CANCELLED";

    const completed =
        order.status === "COMPLETED";

    const orderId = Number(order.id);

    const statusLabel =
        ORDER_STATUS_LABELS[order.status] ||
        order.status;

    const paymentLabel =
        PAYMENT_LABELS[order.payment_method] ||
        order.payment_method;

    const shippingLabel =
        SHIPPING_LABELS[order.fulfillment_type] ||
        order.fulfillment_type;

    const itemsHtml = (order.items || []).map(
        item => `
            <div class="summary-item">
                <span>
                    ${escapeHtml(item.item_name)}
                    x${Number(item.quantity)}
                </span>

                <span>
                    ${formatMoney(Number(item.line_total))}
                </span>
            </div>
        `
    ).join("");

    let html = `
        <div class="result-icon ${cancelled ? "error" : "success"}">
            ${cancelled ? "✕" : "✓"}
        </div>

        <h2 class="${cancelled ? "text-error" : "text-primary"}">
            ${cancelled
                ? "Đơn hàng đã bị hủy"
                : completed
                    ? "Đơn hàng đã hoàn thành"
                    : "Đặt hàng thành công!"
            }
        </h2>

        <p class="muted">
            Mã đơn hàng:
            <strong>#DH${orderId}</strong>
        </p>

        <div style="
            background:var(--color-bg);
            padding:16px;
            border-radius:var(--radius);
            margin:24px 0;
            text-align:left;
        ">

            <p>
                <strong>Trạng thái:</strong>
                ${escapeHtml(statusLabel)}
            </p>

            <p>
                <strong>Người nhận:</strong>
                ${escapeHtml(order.receiver_name || "")}
            </p>

            <p>
                <strong>Số điện thoại:</strong>
                ${escapeHtml(order.receiver_phone || "")}
            </p>

            <p>
                <strong>Địa chỉ:</strong>
                ${escapeHtml(
                    order.shipping_address ||
                    "Nhận tại cửa hàng"
                )}
            </p>

            <p>
                <strong>Thanh toán:</strong>
                ${escapeHtml(paymentLabel)}
            </p>

            <p>
                <strong>Hình thức nhận:</strong>
                ${escapeHtml(shippingLabel)}
            </p>

        </div>

        <div style="text-align:left;">

            <h3>Chi tiết đơn hàng</h3>

            ${itemsHtml}

            <div class="summary-item">
                <span>Tạm tính</span>

                <span>
                    ${formatMoney(Number(order.subtotal))}
                </span>
            </div>

            <div class="summary-item">
                <span>Phí vận chuyển</span>

                <span>
                    ${formatMoney(Number(order.shipping_fee))}
                </span>
            </div>

            <div class="summary-total">
                <span>Tổng cộng</span>

                <strong class="text-primary">
                    ${formatMoney(Number(order.total_amount))}
                </strong>
            </div>

        </div>
    `;

    if (
        order.payment_method === "BANK_TRANSFER" &&
        !cancelled &&
        !completed
    ) {
        html += `
            <div class="status status-loading"
                 style="margin-top:24px; text-align:left;">

                <strong>Lưu ý:</strong>

                Đơn hàng đã được tạo.
                Vui lòng kiểm tra trạng thái thanh toán
                trước khi thực hiện chuyển khoản. <a class="btn" href="../pay.html?id=${Number(order.id)}">Mở thanh toán QR</a>

            </div>
        `;
    }

    html += `
        <div style="
            margin-top:24px;
            display:flex;
            gap:12px;
            justify-content:center;
            flex-wrap:wrap;
        ">

            <a href="products.html"
               class="btn btn-primary">
                Tiếp tục mua sắm
            </a>

            <a href="../index.html"
               class="btn">
                Về trang chủ
            </a>

        </div>
    `;

    container.innerHTML = html;
}

function renderError(container, message) {
    container.innerHTML = `
        <div class="result-icon error">✕</div>

        <h2 class="text-error">
            Không thể tải đơn hàng
        </h2>

        <p class="muted">
            ${escapeHtml(message)}
        </p>

        <div style="margin-top:24px;">

            <button
                id="retry-order-result"
                type="button"
                class="btn btn-primary"
            >
                Thử lại
            </button>

            <a href="../index.html" class="btn">
                Về trang chủ
            </a>

        </div>
    `;

    document.getElementById(
        "retry-order-result"
    ).addEventListener(
        "click",
        loadOrderResult
    );
}

document.addEventListener(
    "DOMContentLoaded",
    loadOrderResult
);
