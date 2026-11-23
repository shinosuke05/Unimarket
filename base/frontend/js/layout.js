const MENU = [
  { href: "index.html", label: "Trang chủ" },
  { href: "pages/items.html", label: "Items" },
  { href: "pages/auth.html", label: "Đăng nhập / Đăng ký" },
  { href: "pages/profile.html", label: "Hồ sơ" },
  { href: "pages/addresses.html", label: "Sổ địa chỉ" },
];

function renderLayout() {
  const root = document.body.dataset.root || "./";
  const currentPath = window.location.pathname;
  const hasToken = Boolean(localStorage.getItem("token"));

  const links = MENU.map((item) => {
    const isActive =
      currentPath.endsWith("/" + item.href) ||
      (item.href === "index.html" && currentPath.endsWith("/"));
    return `<a href="${root}${item.href}" class="${isActive ? "active" : ""}">${item.label}</a>`;
  }).join("");

  const logoutHtml = hasToken
    ? `<button id="btn-logout" type="button" class="btn btn-small btn-danger">Đăng xuất</button>`
    : "";

  document.getElementById("app-header").innerHTML = `
    <div class="container header-inner">
      <a href="${root}index.html" class="brand">
        <img src="${root}assets/images/logo.svg" alt="logo" width="28" height="28">
        <span>${CONFIG.APP_NAME}</span>
      </a>
      <nav class="nav">${links}${logoutHtml}</nav>
    </div>`;

  document.getElementById("app-footer").innerHTML = `
    <div class="container">© ${new Date().getFullYear()} HN-KS25-CNTT1 · Base code thực tập doanh nghiệp</div>`;

  const btnLogout = document.getElementById("btn-logout");
  if (btnLogout) {
    btnLogout.addEventListener("click", () => {
      localStorage.removeItem("token");
      window.location.href = `${root}pages/auth.html`;
    });
  }
}

renderLayout();