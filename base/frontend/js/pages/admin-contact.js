
const $ = id => document.getElementById(id);

const form = $("contact-form");
const notice = $("notice");
const saveButton = $("save");

function showMessage(message, type = "success") {
  notice.hidden = false;
  notice.className = `status ${type === "error" ? "status-error" : "status-ok"}`;
  notice.textContent = message;
}

function showQrPreview() {
  const url = $("qr").value.trim();
  const preview = $("qr-preview");

  if (!url) {
    preview.hidden = true;
    preview.removeAttribute("src");
    return;
  }

  preview.src = url;
  preview.hidden = false;

  preview.onerror = () => {
    preview.hidden = true;
    showMessage("Không thể tải ảnh QR. Kiểm tra lại đường dẫn.", "error");
  };
}

function validate(data) {
  if (data.phone && !/^0\d{9,10}$/.test(data.phone)) {
    return "Số điện thoại không hợp lệ.";
  }

  if (
    data.zalo &&
    !(/^https:\/\/(zalo\.me|chat\.zalo\.me)\/.+/.test(data.zalo) ||
      /^0?\d{9,11}$/.test(data.zalo.replace(/\s/g, "")))
  ) {
    return "Zalo phải là số điện thoại hoặc link zalo.me.";
  }

  if (
    data.facebook_url &&
    !/^https:\/\/(www\.|m\.)?(facebook|fb)\.com\/.+/.test(data.facebook_url)
  ) {
    return "Link Facebook không hợp lệ.";
  }

  if (
    data.qr_image_url &&
    !/^https?:\/\/.+/.test(data.qr_image_url)
  ) {
    return "Link ảnh QR không hợp lệ.";
  }

  if (
    data.bank_account_number &&
    !/^\d{6,20}$/.test(data.bank_account_number)
  ) {
    return "Số tài khoản phải có từ 6 đến 20 chữ số.";
  }

  return "";
}

async function checkAdmin() {
  if (!localStorage.getItem("token")) {
    throw new Error("Bạn chưa đăng nhập. Hãy đăng nhập tài khoản Admin.");
  }

  const user = await api.get("/auth/me");

  if (user.role !== "ADMIN") {
    throw new Error("Tài khoản hiện tại không có quyền Admin.");
  }
}

async function loadSettings() {
  try {
    await checkAdmin();

    const data = await api.get("/store-settings");

    $("phone").value = data.phone || "";
    $("zalo").value = data.zalo || "";
    $("facebook").value = data.facebook_url || "";

    $("bank").value = data.bank_name || "";
    $("account").value = data.bank_account_number || "";
    $("holder").value = data.bank_account_holder || "";
    $("qr").value = data.qr_image_url || "";

    showQrPreview();

    form.hidden = false;
    notice.hidden = true;
  } catch (error) {
    form.hidden = true;
    showMessage(error.message, "error");
  }
}

$("generate-qr").addEventListener("click", () => {
  const bankCode = $("bank-code").value.trim().toUpperCase();
  const account = $("account").value.trim();
  const holder = $("holder").value.trim();

  if (!/^[A-Z0-9]{2,10}$/.test(bankCode)) {
    showMessage("Nhập mã ngân hàng, ví dụ MB hoặc VCB.", "error");
    return;
  }

  if (!/^\d{6,20}$/.test(account)) {
    showMessage("Nhập số tài khoản hợp lệ trước.", "error");
    return;
  }

  $("qr").value =
    `https://img.vietqr.io/image/${bankCode}-${account}-compact2.png?accountName=${encodeURIComponent(holder)}`;

  showQrPreview();
  showMessage("Đã tạo QR. Nhớ bấm Lưu cài đặt.");
});

$("qr").addEventListener("input", showQrPreview);

form.addEventListener("submit", async event => {
  event.preventDefault();

  const data = {
    phone: $("phone").value.trim().replace(/\s/g, ""),
    zalo: $("zalo").value.trim(),
    facebook_url: $("facebook").value.trim(),
    bank_name: $("bank").value.trim(),
    bank_account_number: $("account").value.trim(),
    bank_account_holder: $("holder").value.trim().toUpperCase(),
    qr_image_url: $("qr").value.trim()
  };

  const error = validate(data);

  if (error) {
    showMessage(error, "error");
    return;
  }

  saveButton.disabled = true;
  saveButton.textContent = "Đang lưu...";

  try {
    await api.put("/store-settings", data);
    showMessage("Đã lưu thông tin liên hệ thành công.");
    showQrPreview();
  } catch (error) {
    showMessage(error.message, "error");
  } finally {
    saveButton.disabled = false;
    saveButton.textContent = "Lưu cài đặt";
  }
});

$("reload").addEventListener("click", loadSettings);

loadSettings();
