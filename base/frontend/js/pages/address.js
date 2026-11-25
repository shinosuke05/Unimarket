const addressForm = document.getElementById("address-form");
const addressTableBody = document.getElementById("address-table-body");
const addrCancelBtn = document.getElementById("addr-cancel");
const addrSubmitBtn = document.getElementById("addr-submit");
const addrTitle = document.getElementById("addr-form-title");

let editingAddressId = null;
let currentAddresses = [];

async function loadAddresses() {
  try {
    currentAddresses = await api.get("/addresses");
    renderAddresses(currentAddresses);
  } catch (err) {
    addressTableBody.innerHTML = `<tr><td colspan="4" class="text-error">${escapeHtml(err.message)}</td></tr>`;
  }
}

function renderAddresses(list) {
  if (!list.length) {
    addressTableBody.innerHTML = `<tr><td colspan="4" class="muted">Chưa có địa chỉ</td></tr>`;
    return;
  }
  addressTableBody.innerHTML = list
    .map(
      (a) => `
    <tr>
      <td>
        <strong>${escapeHtml(a.recipient_name)}</strong>
        <div class="muted">${escapeHtml(a.phone)}</div>
      </td>
      <td>${escapeHtml(a.street_address)}</td>
      <td>
        ${
          a.is_default
            ? `<span class="status-ok" style="padding:2px 8px; border-radius:4px; font-size:12px;">Mặc định</span>`
            : `<button class="btn btn-small" data-action="default" data-id="${a.id}">Đặt mặc định</button>`
        }
      </td>
      <td class="actions">
        <button class="btn btn-small" data-action="edit" data-id="${a.id}">Sửa</button>
        <button class="btn btn-small btn-danger" data-action="delete" data-id="${a.id}">Xoá</button>
      </td>
    </tr>`
    )
    .join("");
}

addressForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    recipient_name: addressForm.recipient_name.value.trim(),
    phone: addressForm.phone.value.trim(),
    street_address: addressForm.street_address.value.trim(),
    is_default: addressForm.is_default.checked,
  };
  try {
    if (editingAddressId === null) {
      await api.post("/addresses", payload);
      showToast("Đã thêm địa chỉ");
    } else {
      await api.put(`/addresses/${editingAddressId}`, payload);
      showToast("Đã sửa địa chỉ");
    }
    resetAddressForm();
    loadAddresses();
  } catch (err) {
    showToast(err.message, "error");
  }
});

function startEditAddress(id) {
  const addr = currentAddresses.find((x) => x.id === id);
  if (!addr) return;
  editingAddressId = id;
  addressForm.recipient_name.value = addr.recipient_name;
  addressForm.phone.value = addr.phone;
  addressForm.street_address.value = addr.street_address;
  addressForm.is_default.checked = Boolean(addr.is_default);
  addrTitle.textContent = `Sửa địa chỉ #${id}`;
  addrSubmitBtn.textContent = "Lưu thay đổi";
  addrCancelBtn.hidden = false;
}

function resetAddressForm() {
  editingAddressId = null;
  addressForm.reset();
  addrTitle.textContent = "Thêm địa chỉ";
  addrSubmitBtn.textContent = "Lưu";
  addrCancelBtn.hidden = true;
}

addressTableBody.addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;
  const id = Number(btn.dataset.id);
  const action = btn.dataset.action;

  try {
    if (action === "edit") {
      startEditAddress(id);
    } else if (action === "default") {
      await api.patch(`/addresses/${id}/default`);
      showToast("Đã đặt địa chỉ mặc định");
      loadAddresses();
    } else if (action === "delete") {
      if (!confirm("Xoá địa chỉ này?")) return;
      await api.delete(`/addresses/${id}`);
      showToast("Đã xoá địa chỉ");
      if (editingAddressId === id) resetAddressForm();
      loadAddresses();
    }
  } catch (err) {
    showToast(err.message, "error");
  }
});

addrCancelBtn.addEventListener("click", resetAddressForm);
loadAddresses();