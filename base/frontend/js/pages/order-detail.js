
const params = new URLSearchParams(window.location.search);
const orderId = params.get("id");

const messageElement = document.getElementById("detail-message");
const detailElement = document.getElementById("order-detail");
const cancelButton = document.getElementById("cancel-order");
const confirmReceivedButton = document.getElementById("confirm-received");

const statusLabels = {
  PENDING: "Chờ xác nhận",
  CONFIRMED: "Đã xác nhận",
  SHIPPING: "Đang giao",
  COMPLETED: "Hoàn thành",
  CANCELLED: "Đã huỷ",
};

const timelineSteps = [
  { key: "PENDING", label: "Đã đặt hàng", description: "Đơn hàng đã được ghi nhận." },
  { key: "CONFIRMED", label: "Đã xác nhận", description: "Người bán đã xác nhận đơn hàng." },
  { key: "SHIPPING", label: "Đang giao", description: "Đơn hàng đang được vận chuyển." },
  { key: "COMPLETED", label: "Hoàn thành", description: "Đơn hàng đã giao thành công." },
];

function getStatusIndex(status) {
  return timelineSteps.findIndex((step) => step.key === status);
}

function renderTimeline(order) {
  const history = Array.isArray(order.status_history)
    ? order.status_history
    : Array.isArray(order.histories)
      ? order.histories
      : [];

  const currentIndex = getStatusIndex(order.status);
  const cancelled = order.status === "CANCELLED";

  if (cancelled) {
    document.getElementById("order-timeline").innerHTML = `
      <div class="timeline-item is-done is-cancelled">
        <span class="timeline-dot"></span>
        <div>
          <strong>Đơn hàng đã huỷ</strong>
          <p>Đơn hàng này đã được huỷ.</p>
          ${(history || []).map(h => `<small>${escapeHtml(statusLabels[h.new_status] || h.new_status)} · ${escapeHtml(formatDateTime(h.created_at))} · ${escapeHtml(h.note || "")}</small><br>`).join("")}
        </div>
      </div>`;
    return;
  }

  document.getElementById("order-timeline").innerHTML =
    timelineSteps.map((step, index) => {
      const completed = currentIndex >= index;
      const event = history.find((item) => item.new_status === step.key);

      const date = event?.created_at
        ? formatDateTime(event.created_at)
        : index === 0 && order.created_at
          ? formatDateTime(order.created_at)
          : "";

      return `
        <div class="timeline-item ${completed ? "is-done" : ""} ${index === currentIndex ? "is-current" : ""}">
          <span class="timeline-dot"></span>
          <div>
            <strong>${step.label}</strong>
            <p>${step.description}</p>
            ${date ? `<small>${escapeHtml(date)}</small>` : ""}
          </div>
        </div>`;
    }).join("");
}

function renderItems(items) {
  if (!Array.isArray(items) || !items.length) {
    return '<p class="muted">Không có thông tin sản phẩm.</p>';
  }

  return `<div class="detail-items">${items.map((item) => {
    const name = item.product_name || item.name || `Sản phẩm #${item.product_id || ""}`;
    const price = item.price_at_order ?? item.price ?? 0;
    const quantity = Number(item.quantity || 0);
    const subtotal = item.subtotal ?? Number(price) * quantity;

    return `
      <div class="detail-item">
        <div>
          <strong>${escapeHtml(name)}</strong>
          <span class="muted">${formatMoney(price)} × ${quantity}</span>
        </div>
        <strong>${formatMoney(subtotal)}</strong>
      </div>`;
  }).join("")}</div>`;
}

function renderOrder(order) {
  const status = statusLabels[order.status] || order.status || "Không rõ";

  document.title = `Đơn #${order.id} | UniMarket`;

  document.getElementById("detail-order-code").textContent =
    `Đơn hàng #${order.id}`;

  document.getElementById("detail-created").textContent =
    order.created_at
      ? `Ngày đặt: ${formatDateTime(order.created_at)}`
      : "";

  const statusElement = document.getElementById("detail-status");
  statusElement.textContent = status;
  statusElement.className =
    `order-status status-${String(order.status || "").toLowerCase()}`;

  renderTimeline(order);

  document.getElementById("detail-items").innerHTML =
    renderItems(order.items);

  document.getElementById("detail-total").textContent =
    formatMoney(order.total_amount || 0);

  document.getElementById("detail-recipient").textContent =
    order.recipient || "—";

  document.getElementById("detail-address").textContent =
    order.address || "—";

  document.getElementById("detail-receiving").textContent =
    order.receiving_method === "PICKUP"
      ? "Nhận tại cửa hàng"
      : order.receiving_method === "DELIVERY"
        ? "Giao hàng"
        : "—";

  const paymentLabels = {
    COD: "Thanh toán khi nhận hàng",
    BANK_TRANSFER: "Chuyển khoản",
    E_WALLET: "Ví điện tử",
  };

  document.getElementById("detail-payment").textContent =
    paymentLabels[order.payment_method] || order.payment_method || "—";

  // Chỉ cho huỷ khi đơn đang chờ xác nhận.
  const canCancel = order.status === "PENDING" && !["PAID", "PENDING_CONFIRMATION"].includes(order.payment?.status);
  const pay = document.getElementById("detail-pay-link");
  pay.hidden = order.payment_method !== "BANK_TRANSFER" || order.status === "CANCELLED";
  pay.href = `../pay.html?id=${order.id}`;
  pay.textContent = "Thanh toán QR / Xem trạng thái";
  cancelButton.hidden = !canCancel;

  document.getElementById("cancel-note").textContent = canCancel
    ? "Bạn chỉ có thể huỷ đơn khi đơn hàng đang chờ xác nhận."
    : "Đơn hàng không còn ở trạng thái có thể huỷ.";

  // Chỉ cho xác nhận nhận hàng khi đơn đang giao.
  if (confirmReceivedButton) {
    confirmReceivedButton.hidden = order.status !== "SHIPPING";
  }

  detailElement.hidden = false;
  messageElement.hidden = true;
}

async function loadOrder() {
  if (!orderId || !/^\d+$/.test(orderId)) {
    messageElement.className = "status status-error";
    messageElement.textContent = "Mã đơn hàng không hợp lệ.";
    return;
  }

  try {
    const order = await api.get(
      `/customer/orders/${encodeURIComponent(orderId)}`
    );

    renderOrder(order);
  } catch (error) {
    messageElement.className = "status status-error";

    messageElement.textContent = error.status === 404
      ? "Không tìm thấy đơn hàng."
      : error.status === 401
        ? "Bạn cần đăng nhập để xem đơn hàng."
        : error.message;
  }
}

// Huỷ đơn hàng.
cancelButton.addEventListener("click", async () => {
  if (!confirm("Bạn chắc chắn muốn huỷ đơn hàng này?")) return;

  cancelButton.disabled = true;

  try {
    const result = await api.put(
      `/customer/orders/${encodeURIComponent(orderId)}/cancel`,
      {}
    );

    showToast(result.message || "Đã huỷ đơn hàng");
    await loadOrder();
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    cancelButton.disabled = false;
  }
});

// Xác nhận đã nhận hàng.
if (confirmReceivedButton) {
  confirmReceivedButton.addEventListener("click", async () => {
    if (!confirm("Bạn xác nhận đã nhận được hàng?")) return;

    confirmReceivedButton.disabled = true;

    try {
      const result = await api.post(
        `/customer/orders/${encodeURIComponent(orderId)}/confirm-received`,
        {}
      );

      showToast(result.message || "Đã xác nhận nhận hàng");
      await loadOrder();
    } catch (error) {
      showToast(error.message, "error");
    } finally {
      confirmReceivedButton.disabled = false;
    }
  });
}

loadOrder();
