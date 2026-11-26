
const paymentList = document.getElementById("orders");
const messageBox = document.getElementById("message");
const reloadButton = document.getElementById("reload");

function showPaymentMessage(message, isError = false) {
    if (!messageBox) return;

    messageBox.textContent = message;
    messageBox.style.color = isError ? "red" : "green";
}

function formatPaymentMoney(value) {
    return Number(value || 0).toLocaleString("vi-VN") + " đ";
}

function getPaymentStatus(status) {
    const statuses = {
        UNPAID: "Chưa thanh toán",
        PENDING_CONFIRMATION: "Chờ xác nhận",
        PAID: "Đã thanh toán",
        FAILED: "Thất bại",
    };

    return statuses[status] || status || "Chưa thanh toán";
}

function renderPayments(orders) {
    if (!paymentList) return;

    const pendingOrders = orders.filter(order =>
        order.payment &&
        order.payment.status === "PENDING_CONFIRMATION"
    );

    if (pendingOrders.length === 0) {
        paymentList.innerHTML = `
            <tr>
                <td colspan="7" style="text-align:center">
                    Không có giao dịch nào đang chờ xác nhận
                </td>
            </tr>
        `;
        return;
    }

    paymentList.innerHTML = pendingOrders.map(order => `
        <tr>
            <td>DH${order.id}</td>
            <td>${escapePaymentText(order.recipient || "")}</td>
            <td>${escapePaymentText(order.receiver_phone || "")}</td>
            <td>${formatPaymentMoney(order.total_amount)}</td>
            <td>${escapePaymentText(order.payment.transfer_note || "")}</td>
            <td>${getPaymentStatus(order.payment.status)}</td>
            <td>
                <button
                    type="button"
                    onclick="confirmPayment(${order.id})"
                >
                    Xác nhận
                </button>

                <button
                    type="button"
                    onclick="rejectPayment(${order.id})"
                >
                    Từ chối
                </button>
            </td>
        </tr>
    `).join("");
}

function escapePaymentText(value) {
    return String(value).replace(/[&<>"']/g, character => {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
        };

        return entities[character];
    });
}

async function loadPayments() {
    try {
        showPaymentMessage("Đang tải giao dịch...");

        const response = await api.get("/admin/orders/");
        const orders = Array.isArray(response)
            ? response
            : response.items || response.data || [];

        renderPayments(orders);

        showPaymentMessage(
            `Đã tải ${orders.length} đơn hàng.`
        );
    } catch (error) {
        console.error(error);
        showPaymentMessage(
            "Không tải được danh sách thanh toán. Hãy kiểm tra quyền admin.",
            true
        );
    }
}

async function confirmPayment(orderId) {
    const accepted = confirm(
        `Xác nhận đã nhận tiền cho đơn DH${orderId}?`
    );

    if (!accepted) return;

    try {
        await api.put(
            `/admin/orders/${orderId}/payment/confirm`
        );

        showPaymentMessage(
            `Đã xác nhận thanh toán đơn DH${orderId}.`
        );

        await loadPayments();
    } catch (error) {
        console.error(error);
        showPaymentMessage(
            "Không thể xác nhận thanh toán.",
            true
        );
    }
}

async function rejectPayment(orderId) {
    const accepted = confirm(
        `Từ chối giao dịch của đơn DH${orderId}?`
    );

    if (!accepted) return;

    try {
        await api.put(
            `/admin/orders/${orderId}/payment/reject`
        );

        showPaymentMessage(
            `Đã từ chối thanh toán đơn DH${orderId}.`
        );

        await loadPayments();
    } catch (error) {
        console.error(error);
        showPaymentMessage(
            "Không thể từ chối thanh toán.",
            true
        );
    }
}

if (reloadButton) {
    reloadButton.addEventListener("click", loadPayments);
}

loadPayments();
