const listElement = document.getElementById("orders-list");
const messageElement = document.getElementById("orders-message");
const searchElement = document.getElementById("order-search");
const filterElement = document.getElementById("status-filter");

const statusLabels = {
  PENDING: "Chờ xác nhận",
  CONFIRMED: "Đã xác nhận",
  SHIPPING: "Đang giao",
  COMPLETED: "Hoàn thành",
  CANCELLED: "Đã huỷ",
};

let allOrders = [];

function orderStatusClass(status) {
  return `status-${String(status || "").toLowerCase()}`;
}

function renderOrders() {
  const keyword = searchElement.value.trim().toLowerCase();
  const selectedStatus = filterElement.value;
  const filtered = allOrders.filter((order) => {
    const matchesCode = String(order.id).toLowerCase().includes(keyword);
    const matchesStatus = !selectedStatus || order.status === selectedStatus;
    return matchesCode && matchesStatus;
  });

  if (!filtered.length) {
    listElement.innerHTML = '<div class="empty-orders">Không tìm thấy đơn hàng phù hợp.</div>';
    return;
  }

  listElement.innerHTML = filtered.map((order) => {
    const count = (order.items || []).reduce((sum, item) => sum + Number(item.quantity || 0), 0);
    const created = order.created_at ? formatDateTime(order.created_at) : "—";
    const status = statusLabels[order.status] || order.status || "Không rõ";
    return `
      <article class="order-card">
        <div class="order-card-top">
          <div>
            <span class="muted">Mã đơn hàng</span>
            <strong class="order-code">#${escapeHtml(order.id)}</strong>
          </div>
          <span class="order-status ${orderStatusClass(order.status)}">${escapeHtml(status)}</span>
        </div>
        <div class="order-card-info">
          <span>${count} sản phẩm</span>
          <span>Đặt lúc ${escapeHtml(created)}</span>
        </div>
        <div class="order-card-bottom">
          <div><span class="muted">Tổng tiền</span><strong>${formatMoney(order.total_amount || 0)}</strong></div>
          <a class="btn btn-primary btn-small" href="order-detail.html?id=${encodeURIComponent(order.id)}">Xem chi tiết</a>
        </div>
      </article>`;
  }).join("");
}

async function loadOrders() {
  messageElement.hidden = false;
  messageElement.className = "status status-loading";
  messageElement.textContent = "Đang tải đơn hàng...";
  listElement.innerHTML = "";

  try {
    const data = await api.get("/customer/orders/");
    allOrders = Array.isArray(data) ? data : [];
    messageElement.hidden = true;
    renderOrders();
  } catch (error) {
    messageElement.className = "status status-error";
    messageElement.textContent = error.status === 401
      ? "Bạn cần đăng nhập để xem đơn hàng."
      : error.message;
  }
}

searchElement.addEventListener("input", renderOrders);
filterElement.addEventListener("change", renderOrders);
loadOrders();
