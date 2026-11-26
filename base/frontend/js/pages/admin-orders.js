
const orderBody = document.getElementById("orders");
const message = document.getElementById("message");
const keywordInput = document.getElementById("keyword");
const statusInput = document.getElementById("status");

let allOrders = [];

const statusNames = {
  PENDING: "Chờ xác nhận",
  CONFIRMED: "Đã xác nhận",
  SHIPPING: "Đang giao",
  COMPLETED: "Hoàn thành",
  CANCELLED: "Đã hủy"
};

const paymentNames = {
  UNPAID: "Chưa thanh toán",
  PENDING_CONFIRMATION: "Chờ xác nhận",
  PAID: "Đã thanh toán",
  FAILED: "Thất bại"
};

async function loadOrders() {
  message.hidden = false;
  message.textContent = "Đang tải đơn hàng...";
  orderBody.innerHTML = "";

  try {
    const params = {};
    if (statusInput.value) params.status = statusInput.value;
    if (keywordInput.value.trim()) params.keyword = keywordInput.value.trim();

    allOrders = await api.get("/admin/orders/", params);
    renderOrders();
    message.hidden = true;
  } catch (error) {
    message.textContent = error.message;
    message.className = "status status-error";
  }
}

function renderOrders() {
  const keyword = keywordInput.value.trim().toLowerCase();

  const filtered = allOrders.filter(order => {
    const text = `${order.id} ${order.recipient || ""} ${order.receiver_phone || ""}`.toLowerCase();
    return text.includes(keyword);
  });

  if (!filtered.length) {
    orderBody.innerHTML = '<tr><td colspan="7">Không có đơn hàng.</td></tr>';
    return;
  }

  orderBody.innerHTML = filtered.map(order => {
    const paymentStatus = order.payment?.status || "UNPAID";
    const status = order.status;

    let actions = `<button class="btn btn-small" data-action="detail" data-id="${order.id}">Chi tiết</button>`;

    if (status === "PENDING") {
      actions += ` <button class="btn btn-primary btn-small" data-action="confirm" data-id="${order.id}">Xác nhận đơn</button>`;
      actions += ` <button class="btn btn-danger btn-small" data-action="cancel" data-id="${order.id}">Hủy đơn</button>`;
    }

    if (status === "CONFIRMED") {
      actions += ` <button class="btn btn-primary btn-small" data-action="shipping" data-id="${order.id}">Bắt đầu giao</button>`;
    }

    if (status === "SHIPPING") {
      actions += ` <button class="btn btn-primary btn-small" data-action="complete" data-id="${order.id}">Hoàn thành</button>`;
    }

    return `
      <tr>
        <td>#${escapeHtml(order.id)}</td>
        <td>${escapeHtml(order.recipient || "—")}</td>
        <td>${escapeHtml(order.receiver_phone || "—")}</td>
        <td>${formatMoney(order.total_amount || 0)}</td>
        <td>${paymentNames[paymentStatus] || paymentStatus}</td>
        <td>${statusNames[status] || status}</td>
        <td class="actions">${actions}</td>
      </tr>`;
  }).join("");
}

orderBody.addEventListener("click", async event => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const id = button.dataset.id;
  const action = button.dataset.action;

  if (action === "detail") {
    window.location.href = `admin-order-detail.html?id=${id}`;
    return;
  }

  if (!confirm("Mày chắc chắn muốn thực hiện thao tác này?")) return;

  button.disabled = true;

  try {
    if (action === "confirm") {
      await api.put(`/admin/orders/${id}/confirm`);
    } else if (action === "cancel") {
      await api.put(`/admin/orders/${id}/reject`);
    } else if (action === "shipping") {
      await api.put(`/admin/orders/${id}/status?new_status=SHIPPING`);
    } else if (action === "complete") {
      await api.put(`/admin/orders/${id}/complete`);
    }

    showToast("Đã cập nhật đơn hàng");
    await loadOrders();
  } catch (error) {
    showToast(error.message, "error");
    button.disabled = false;
  }
});

document.getElementById("reload").addEventListener("click", loadOrders);
statusInput.addEventListener("change", loadOrders);
keywordInput.addEventListener("input", renderOrders);

loadOrders();
