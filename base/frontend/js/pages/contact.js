// File: base/frontend/js/pages/contact.js
(async function () {
  const C = window.Contact, app = document.getElementById("app");
  try {
    const s = await C.fetchContact();
    const qr = C.assetUrl(s.qr_image_url);
    app.innerHTML = `
      <h1>Liên hệ UniMarket</h1>
      <p class="cmute">Cần tư vấn hoặc hỗ trợ đơn hàng? Chọn cách liên hệ bạn thấy tiện nhất.</p>
      <div class="grid3">
        ${s.phone ? `<a class="ct" href="${C.esc(C.telHref(s.phone))}"><div class="ic tel">☎</div><b>Gọi điện</b><span>${C.esc(C.fmtPhone(s.phone))}</span></a>` : ""}
        ${s.zalo ? `<a class="ct" href="${C.esc(C.zaloHref(s.zalo))}" target="_blank" rel="noopener noreferrer"><div class="ic zalo">Z</div><b>Chat Zalo</b><span>${C.esc(s.zalo)}</span></a>` : ""}
        ${s.facebook_url ? `<a class="ct" href="${C.esc(s.facebook_url)}" target="_blank" rel="noopener noreferrer"><div class="ic fb">f</div><b>Facebook</b><span>${C.esc(s.facebook_url.replace(/^https?:\/\//, ""))}</span></a>` : ""}
      </div>
      ${qr || s.bank_account_number ? `
      <div class="card"><h2>Chuyển khoản qua QR</h2>
        <div class="qr">${qr ? `<img src="${C.esc(qr)}" alt="Mã QR chuyển khoản">` : ""}
          <div>
            <div class="line"><span class="cmute">Ngân hàng</span><b>${C.esc(s.bank_name || "—")}</b></div>
            <div class="line"><span class="cmute">Số tài khoản</span><span><span class="mono">${C.esc(s.bank_account_number || "—")}</span> ${s.bank_account_number ? `<button class="small" data-copy="${C.esc(s.bank_account_number)}">Sao chép</button>` : ""}</span></div>
            <div class="line"><span class="cmute">Chủ tài khoản</span><b>${C.esc(s.bank_account_holder || "—")}</b></div>
          </div></div></div>` : ""}`;
  } catch (e) {
    app.innerHTML = `<p class="empty">${C.esc(e.message)}<br>Hãy kiểm tra backend đang chạy.</p>`;
  }
  document.addEventListener("click", (e) => {
    const v = e.target.dataset && e.target.dataset.copy;
    if (v && navigator.clipboard) navigator.clipboard.writeText(v).then(() => C.toast("Đã sao chép " + v));
  });
})();