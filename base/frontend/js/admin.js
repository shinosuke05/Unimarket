/* Layout admin + chặn người không phải admin.
 * Lưu ý: chặn ở FE chỉ để giao diện gọn; bảo vệ thật nằm ở BE (require_admin). */
(function () {
  const API_BASE = "http://127.0.0.1:8000/api"; // đổi khi deploy
  const TOKEN_KEY = "unimarket_token";
  const LOGIN_URL = "login.html";

  const MENU = [
    { key: "dashboard", label: "Dashboard", href: "index.html", icon: "📊" },
    { key: "categories", label: "Danh mục", href: "categories.html", icon: "🗂️" },
    { key: "products", label: "Sản phẩm", href: "products.html", icon: "📦" },
    { key: "orders", label: "Đơn hàng", href: "orders.html", icon: "🧾" },
    { key: "customers", label: "Khách hàng", href: "customers.html", icon: "👥" },
    { key: "settings", label: "Cài đặt liên hệ", href: "settings.html", icon: "☎️" },
  ];

  function logout(denied) {
    localStorage.removeItem(TOKEN_KEY);
    location.replace(LOGIN_URL + (denied ? "?denied=1" : ""));
  }

  async function api(path, options = {}) {
    const token = localStorage.getItem(TOKEN_KEY);
    const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
    if (token) headers.Authorization = "Bearer " + token;

    const res = await fetch(API_BASE + path, { ...options, headers });
    if (res.status === 401) {
      logout(false);
      throw new Error("Phiên đăng nhập đã hết hạn");
    }
    if (!res.ok) {
      let detail = "";
      try { detail = (await res.json()).detail; } catch (e) { /* bỏ qua */ }
      if (res.status === 403) { logout(true); }
      throw new Error(typeof detail === "string" && detail ? detail : "Lỗi " + res.status);
    }
    return res.status === 204 ? null : res.json();
  }

  function buildLayout(user) {
    const current = document.body.dataset.page;
    const links = MENU.map(
      (m) => `<a href="${m.href}" class="${m.key === current ? "active" : ""}"><span>${m.icon}</span>${m.label}</a>`
    ).join("");

    const shell = document.createElement("div");
    shell.className = "admin-shell";
    shell.innerHTML = `
      <aside class="sidebar" id="sidebar">
        <div class="brand">Unimarket Admin</div>
        <nav>${links}</nav>
      </aside>
      <div class="backdrop" id="backdrop"></div>
      <div class="main-col">
        <header class="topbar">
          <button id="menuBtn" aria-label="Mở menu">☰</button>
          <h1 id="pageTitle"></h1>
          <div class="user"><span id="userName"></span><button id="logoutBtn">Đăng xuất</button></div>
        </header>
      </div>`;

    shell.querySelector("#pageTitle").textContent = document.body.dataset.title || "";
    shell.querySelector("#userName").textContent = user.full_name;

    const content = document.getElementById("content");
    content.classList.add("content");
    shell.querySelector(".main-col").appendChild(content);
    document.body.appendChild(shell);

    const closeMenu = () => document.body.classList.remove("menu-open");
    shell.querySelector("#menuBtn").addEventListener("click", () => document.body.classList.toggle("menu-open"));
    shell.querySelector("#backdrop").addEventListener("click", closeMenu);
    shell.querySelector("#logoutBtn").addEventListener("click", () => logout(false));
    window.addEventListener("resize", () => { if (window.innerWidth > 900) closeMenu(); });
  }

  async function init() {
    if (!localStorage.getItem(TOKEN_KEY)) return logout(false);

    let user;
    try {
      user = await api("/auth/me");
    } catch (e) {
      if (e instanceof TypeError) { // fetch lỗi mạng: server chưa chạy
        document.body.classList.add("ready");
        document.body.textContent = "Không kết nối được máy chủ. Hãy chạy backend rồi tải lại trang.";
      }
      return;
    }
    if (user.role !== "ADMIN") return logout(true);

    window.AdminApp.user = user;
    buildLayout(user);
    document.body.classList.add("ready");
    document.dispatchEvent(new CustomEvent("admin:ready", { detail: { user } }));
  }

  window.AdminApp = { api, logout, user: null };
  if (document.body.dataset.page) init();
})();