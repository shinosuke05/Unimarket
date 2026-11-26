// File: base/frontend/js/pages/admin-contact.js
// Dùng API có sẵn: GET /api/store-settings (công khai) và PUT /api/store-settings (chỉ ADMIN).
(async function () {
  const C = window.Contact, A = C.API_BASE, app = document.getElementById("app");
  const token = () => localStorage.getItem("token") || localStorage.getItem("access_token") || ""; // đổi nếu trang đăng nhập lưu tên khác
  const headers = () => ({ "Content-Type": "application/json", Authorization: "Bearer " + token() });
  const $ = (id) => document.getElementById(id);
  const msg = (e) => (typeof e === "string" ? e : Array.isArray(e) ? (e[0].msg || "").replace("Value error, ", "") : "Có lỗi xảy ra");

  async function api(path, opts) {
    const res = await fetch(A + path, opts);
    const data = await res.json().catch(() => null);
    if (!res.ok) throw new Error(msg(data && data.detail));
    return data;
  }

  try {
    if (!token()) throw new Error("Bạn cần đăng nhập tài khoản admin.");
    const me = await api("/auth/me", { headers: headers() });
    if (me.role !== "ADMIN") throw new Error("Chỉ quản trị viên mới dùng được trang này.");
  } catch (e) { app.innerHTML = `<p class="empty">${C.esc(e.message)}</p>`; return; }

  const s = await C.fetchContact();
  app.innerHTML = `
    <h1>Cập nhật thông tin liên hệ & QR</h1>
    <p class="cmute">Thay đổi áp dụng ngay cho trang Liên hệ, trang thanh toán QR và nút liên hệ ở chi tiết sản phẩm.</p>
    <div class="card"><h2>Liên hệ</h2>
      <div class="two"><div><label for="phone">Số điện thoại</label><input id="phone" type="tel" value="${C.esc(s.phone)}" placeholder="0912345678"></div>
      <div><label for="zalo">Zalo (số hoặc link zalo.me)</label><input id="zalo" value="${C.esc(s.zalo)}" placeholder="0912345678"></div></div>
      <label for="fb">Link Facebook</label><input id="fb" type="url" value="${C.esc(s.facebook_url)}" placeholder="https://facebook.com/ten-trang"></div>
    <div class="card"><h2>Tài khoản ngân hàng & QR</h2>
      <div class="two"><div><label for="bank">Ngân hàng</label><input id="bank" value="${C.esc(s.bank_name)}" placeholder="MB Bank"></div>
      <div><label for="acc">Số tài khoản</label><input id="acc" value="${C.esc(s.bank_account_number)}" inputmode="numeric"></div></div>
      <label for="holder">Chủ tài khoản</label><input id="holder" value="${C.esc(s.bank_account_holder)}">
      <label for="qrurl">Link ảnh mã QR</label>
      <input id="qrurl" type="url" value="${C.esc(s.qr_image_url)}" placeholder="https://...">
      <div class="two"><div><label for="code">Hoặc tạo QR tự động: mã ngân hàng (MB, VCB, TCB, ACB...)</label>
        <input id="code" placeholder="MB" maxlength="10"></div>
        <div style="align-self:end"><button class="ghost" id="gen" type="button">Tạo QR từ số tài khoản</button></div></div>
      <div class="up" style="margin-top:.8rem"><img id="prev" alt="Xem trước mã QR" style="display:none"><span class="cmute" id="prevnote">Chưa có ảnh QR</span></div></div>
    <button id="save">Lưu thay đổi</button>`;

  function showPreview() {
    const u = $("qrurl").value.trim(), img = $("prev");
    if (!u) { img.style.display = "none"; $("prevnote").textContent = "Chưa có ảnh QR"; return; }
    img.src = C.assetUrl(u); img.style.display = ""; $("prevnote").textContent = "Xem trước";
    img.onerror = () => { img.style.display = "none"; $("prevnote").textContent = "Không tải được ảnh từ link này"; };
  }
  $("qrurl").oninput = showPreview; showPreview();

  $("gen").onclick = () => {
    const code = $("code").value.trim().toUpperCase(), acc = $("acc").value.trim();
    if (!/^[A-Z0-9]{2,10}$/.test(code)) return C.toast("Nhập mã ngân hàng, ví dụ MB hoặc VCB");
    if (!/^\d{6,20}$/.test(acc)) return C.toast("Nhập số tài khoản (6–20 chữ số) trước");
    $("qrurl").value = `https://img.vietqr.io/image/${code}-${acc}-compact2.png?accountName=${encodeURIComponent($("holder").value.trim())}`;
    showPreview(); C.toast("Đã tạo link QR, bấm Lưu để áp dụng");
  };

  function validate(b) {
    if (b.phone && !/^0\d{8,10}$/.test(b.phone.replace(/\s/g, ""))) return "Số điện thoại không hợp lệ (vd 0912345678)";
    if (b.zalo && !(/^https?:\/\/(zalo\.me|chat\.zalo\.me)\/.+/.test(b.zalo) || /^0?\d{9,11}$/.test(b.zalo.replace(/\s/g, "")))) return "Zalo: nhập số điện thoại hoặc link zalo.me";
    if (b.facebook_url && !/^https:\/\/(www\.|m\.)?(facebook|fb)\.com\/.+/.test(b.facebook_url)) return "Link Facebook phải bắt đầu bằng https://facebook.com/";
    if (b.bank_account_number && !/^\d{6,20}$/.test(b.bank_account_number)) return "Số tài khoản gồm 6–20 chữ số";
    if (b.qr_image_url && !/^https?:\/\/.+/.test(b.qr_image_url)) return "Link ảnh QR phải bắt đầu bằng https://";
    return "";
  }

  $("save").onclick = async () => {
    const body = { phone: $("phone").value.trim().replace(/\s/g, ""), zalo: $("zalo").value.trim(), facebook_url: $("fb").value.trim(),
      bank_name: $("bank").value.trim(), bank_account_number: $("acc").value.trim(), bank_account_holder: $("holder").value.trim().toUpperCase(),
      qr_image_url: $("qrurl").value.trim() };
    const err = validate(body);
    if (err) return C.toast(err);
    try { await api("/store-settings", { method: "PUT", headers: headers(), body: JSON.stringify(body) }); C.toast("Đã lưu thông tin liên hệ"); }
    catch (e) { C.toast(e.message); }
  };
})();