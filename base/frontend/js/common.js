// ĐỔI địa chỉ backend ở đây nếu khác
const API = "http://127.0.0.1:8000/api";
const $ = (s, r = document) => r.querySelector(s);
const params = new URLSearchParams(location.search);

async function api(path, opts = {}) {
  const token = localStorage.getItem("token");
  const res = await fetch(API + path, {
    ...opts,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: "Bearer " + token } : {}) },
  });
  if (res.status === 401) { localStorage.removeItem("token"); location.href = "login.html"; throw new Error("Chưa đăng nhập"); }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error(typeof data?.detail === "string" ? data.detail : "Có lỗi xảy ra, thử lại sau");
  return data;
}
const post = (path, body) => api(path, { method: "POST", body: body ? JSON.stringify(body) : undefined });

const money = (n) => Number(n).toLocaleString("vi-VN") + " ₫";
const fmtDate = (s) => new Date(s).toLocaleString("vi-VN");
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const STATUS = {
  PENDING: ["Chờ xác nhận", "warn"], CONFIRMED: ["Đã xác nhận", "info"],
  SHIPPING: ["Đang giao", "info"], COMPLETED: ["Hoàn thành", "ok"], CANCELLED: ["Đã huỷ", "gray"],
};
const PAY = {
  UNPAID: ["Chưa thanh toán", "bad"], PENDING_CONFIRMATION: ["Chờ xác nhận", "warn"], PAID: ["Đã thanh toán", "ok"],
};
const METHOD = { COD: "Tiền mặt khi nhận hàng", BANK_TRANSFER: "Chuyển khoản", QR: "Quét mã QR" };
const badge = (map, key) => `<span class="badge ${map[key][1]}">${map[key][0]}</span>`;

function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.style.display = "block";
  clearTimeout(toast.id); toast.id = setTimeout(() => (t.style.display = "none"), 2800);
}
function layout(title) {
  document.body.insertAdjacentHTML("afterbegin",
    `<header class="top"><b>Chợ đồ cũ sinh viên</b><a href="orders.html">Đơn của tôi</a><a href="admin-orders.html">Quản trị</a></header>`);
  document.body.insertAdjacentHTML("beforeend", `<div id="toast" role="status"></div>`);
  document.title = title;
}