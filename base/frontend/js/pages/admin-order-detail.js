
const params = new URLSearchParams(location.search);
const orderId = params.get("id");

const message = document.getElementById("message");
const detail = document.getElementById("detail");

async function loadDetail() {
  if (!orderId || !/^\d+$/.test(orderId)) {
    message.textContent = "Mã đơn hàng không hợp lệ.";
    return;
  }

  try {
    const order = await api.get(`/admin/orders/${orderId}`);

    document.getElementById("code").textContent = `Đơn hàng #${order.id}`;
    document.getElementById("customer").textContent =
      `Người nhận: ${order.recipient || "—"}`;
    document.getElementById("phone").textContent =
      `Điện thoại: ${order.receiver_phone || "—"}`;
    document.getElementById("address").textContent =
      `Địa chỉ: ${order.address || "—"}`;
    document.getElementById("payment").textContent =
      `Thanh toán: ${order.payment?.status || "UNPAID"}`;
    document.getElementById("status").textContent =
      `Trạng thái: ${order.status}`;

    document.getElementById("items").innerHTML =
      (order.items || []).map(item => `
        <div class="line">
          <span>${escapeHtml(item.product_name || item.name || "Sản phẩm")} × ${item.quantity}</span>
          <strong>${formatMoney(item.subtotal || 0)}</strong>
        </div>
      `).join("") || "Không có sản phẩm.";

    document.getElementById("total").textContent =
      `Tổng tiền: ${formatMoney(order.total_amount || 0)}`;

    message.hidden = true;
    detail.hidden = false;
  } catch (error) {
    message.className = "status status-error";
    message.textContent = error.message;
  }
}

loadDetail();
