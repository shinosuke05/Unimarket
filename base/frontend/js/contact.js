// File: base/frontend/js/contact.js
// Dùng chung: lấy thông tin liên hệ và vẽ nút Gọi / Zalo / Facebook.
// Gắn vào bất kỳ trang nào bằng:  <div data-contact-buttons></div>  +  <script src="../js/contact.js"></script>
(function () {
  // Nếu nhóm đã có js/config.js, đặt window.API_BASE ở đó (vd "http://127.0.0.1:8000/api") trước khi nạp file này.
  const API_BASE = window.API_BASE || "http://127.0.0.1:8000/api";
  const API_ORIGIN = API_BASE.replace(/\/api\/?$/, "");

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const telHref = (p) => "tel:" + String(p || "").replace(/[^\d+]/g, "");
  const zaloHref = (z) => { z = String(z || "").trim(); return /^https?:\/\//.test(z) ? z : "https://zalo.me/" + z.replace(/\D/g, ""); };
  const assetUrl = (u) => (!u ? "" : /^https?:\/\//.test(u) ? u : API_ORIGIN + u);
  const fmtPhone = (p) => String(p || "").replace(/\D/g, "").replace(/(\d{4})(\d{3})(\d+)/, "$1 $2 $3");

  async function fetchContact() {
    const res = await fetch(API_BASE + "/store-settings");
    if (!res.ok) throw new Error("Không tải được thông tin liên hệ (HTTP " + res.status + ")");
    return res.json();
  }

  function buttonsHtml(s) {
    const b = [];
    if (s.phone) b.push(`<a class="cbtn tel" href="${esc(telHref(s.phone))}">☎ Gọi ngay</a>`);
    if (s.zalo) b.push(`<a class="cbtn zalo" href="${esc(zaloHref(s.zalo))}" target="_blank" rel="noopener noreferrer">Z Chat Zalo</a>`);
    if (s.facebook_url) b.push(`<a class="cbtn fb" href="${esc(s.facebook_url)}" target="_blank" rel="noopener noreferrer">f Facebook</a>`);
    return b.join("") || `<span class="cmute">Cửa hàng chưa cập nhật thông tin liên hệ.</span>`;
  }

  async function mount() {
    const els = document.querySelectorAll("[data-contact-buttons]");
    if (!els.length) return;
    els.forEach((el) => el.classList.add("contact-buttons"));
    try {
      const s = await fetchContact();
      els.forEach((el) => (el.innerHTML = buttonsHtml(s)));
    } catch (e) {
      els.forEach((el) => (el.innerHTML = `<span class="cmute">${esc(e.message)}</span>`));
    }
  }
  document.addEventListener("DOMContentLoaded", mount);

  function toast(msg) {
    let t = document.getElementById("toast");
    if (!t) { t = document.createElement("div"); t.id = "toast"; document.body.appendChild(t); }
    t.textContent = msg; t.style.display = "block";
    clearTimeout(toast.t); toast.t = setTimeout(() => (t.style.display = "none"), 3000);
  }

  window.Contact = { API_BASE, esc, telHref, zaloHref, assetUrl, fmtPhone, fetchContact, buttonsHtml, toast };
})();