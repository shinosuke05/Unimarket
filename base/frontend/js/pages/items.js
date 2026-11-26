
"use strict";

const form = document.getElementById("item-form");
const tableBody = document.getElementById("item-table-body");
const searchInput = document.getElementById("search-input");
const formTitle = document.getElementById("form-title");
const submitButton = document.getElementById("btn-submit");
const cancelButton = document.getElementById("btn-cancel");

let editingId = null;
let actionBusy = false;
let searchTimer;

// ==================== DANH SÁCH ====================

async function loadItems() {
  tableBody.innerHTML = `
    <tr>
      <td colspan="5" class="muted">Đang tải...</td>
    </tr>
  `;

  try {
    const keyword = searchInput.value.trim();

    const items = await api.get(
      "/items",
      keyword ? { q: keyword } : undefined
    );

    renderItems(items);

  } catch (error) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="5" class="text-error">
          ${escapeHtml(error.message)}
        </td>
      </tr>
    `;
  }
}

function renderItems(items) {
  if (!items.length) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="5" class="muted">
          Chưa có dữ liệu
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = items.map(item => {
    const available =
      item.status === "AVAILABLE" &&
      Number(item.quantity) > 0;

    return `
      <tr>
        <td>${Number(item.id)}</td>

        <td>
          <strong>${escapeHtml(item.name)}</strong>

          <div class="muted">
            ${escapeHtml(item.description || "")}
          </div>

          <div class="muted">
            Tồn kho: ${Number(item.quantity)}
          </div>
        </td>

        <td class="text-right">
          ${formatMoney(Number(item.price))}
        </td>

        <td>${formatDateTime(item.created_at)}</td>

        <td class="actions">
          <button
            class="btn btn-small btn-primary"
            data-action="add-cart"
            data-id="${Number(item.id)}"
            ${available ? "" : "disabled"}
          >
            Thêm vào giỏ
          </button>

          <button
            class="btn btn-small btn-primary"
            data-action="buy-now"
            data-id="${Number(item.id)}"
            ${available ? "" : "disabled"}
          >
            Mua ngay
          </button>

          <button
            class="btn btn-small"
            data-action="edit"
            data-id="${Number(item.id)}"
          >
            Sửa
          </button>

          <button
            class="btn btn-small btn-danger"
            data-action="delete"
            data-id="${Number(item.id)}"
          >
            Xóa
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

// ==================== THÊM / SỬA ====================

form.addEventListener("submit", async event => {
  event.preventDefault();

  const data = {
    name: form.name.value.trim(),
    description: form.description.value.trim() || null,
    price: Number(form.price.value || 0)
  };

  submitButton.disabled = true;

  try {
    if (editingId === null) {
      await api.post("/items", data);
      showToast("Đã thêm sản phẩm");
    } else {
      await api.put(`/items/${editingId}`, data);
      showToast("Đã cập nhật sản phẩm");
    }

    resetForm();
    await loadItems();

  } catch (error) {
    showToast(error.message, "error");
  } finally {
    submitButton.disabled = false;
  }
});

async function startEdit(id) {
  try {
    const item = await api.get(`/items/${id}`);

    editingId = id;

    form.name.value = item.name;
    form.description.value = item.description || "";
    form.price.value = item.price;

    formTitle.textContent = `Sửa item #${id}`;
    submitButton.textContent = "Lưu thay đổi";
    cancelButton.hidden = false;

    form.name.focus();

  } catch (error) {
    showToast(error.message, "error");
  }
}

function resetForm() {
  editingId = null;

  form.reset();

  formTitle.textContent = "Thêm item mới";
  submitButton.textContent = "Thêm";
  cancelButton.hidden = true;
}

// ==================== XÓA ====================

async function deleteItem(id) {
  if (!confirm(`Xóa item #${id}?`)) return;

  try {
    await api.delete(`/items/${id}`);

    showToast("Đã xóa sản phẩm");

    if (editingId === id) {
      resetForm();
    }

    await loadItems();

  } catch (error) {
    showToast(error.message, "error");
  }
}

// ==================== GIỎ HÀNG ====================

async function addToCart(id) {
  if (!localStorage.getItem("token")) {
    showToast("Bạn cần đăng nhập trước", "error");
    window.location.href = "auth.html";
    return;
  }

  try {
    await api.post("/cart/items", {
      product_id: id,
      quantity: 1
    });

    if (window.updateCartBadge) {
      window.updateCartBadge();
    }

    showToast("Đã thêm sản phẩm vào giỏ hàng");

  } catch (error) {
    showToast(error.message, "error");
  }
}

// ==================== MUA NGAY ====================

async function buyNow(id) {
  if (!localStorage.getItem("token")) {
    showToast("Bạn cần đăng nhập trước", "error");
    window.location.href = "auth.html";
    return;
  }

  window.location.href =
    `checkout.html?mode=buy-now&item_id=${encodeURIComponent(id)}&quantity=1`;
}

// ==================== SỰ KIỆN ====================

tableBody.addEventListener("click", async event => {
  const button = event.target.closest(
    "button[data-action]"
  );

  if (!button || actionBusy) return;

  const id = Number(button.dataset.id);
  const action = button.dataset.action;

  if (!Number.isSafeInteger(id) || id < 1) return;

  actionBusy = true;
  button.disabled = true;

  try {
    switch (action) {
      case "edit":
        await startEdit(id);
        break;

      case "delete":
        await deleteItem(id);
        break;

      case "add-cart":
        await addToCart(id);
        break;

      case "buy-now":
        await buyNow(id);
        break;
    }
  } finally {
    actionBusy = false;
    button.disabled = false;
  }
});

cancelButton.addEventListener("click", resetForm);

searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadItems, 300);
});

loadItems();
