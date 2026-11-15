// Layout chung: tự chèn header (menu) và footer vào mọi trang,
// để không phải copy lại HTML menu ở từng file.
//
// Mỗi trang cần có:  <body data-root="./">   (trang ở thư mục gốc)
//              hoặc  <body data-root="../">  (trang trong thư mục pages/)
// và hai thẻ rỗng:   <header id="app-header"></header> ... <footer id="app-footer"></footer>

// Thêm trang mới vào menu: thêm 1 dòng vào mảng này (đường dẫn tính từ thư mục frontend/)
// js/layout.js

// Thêm trang Giỏ hàng vào menu
const MENU = [
  { href: "index.html", label: "Trang chủ" },
  { href: "pages/items.html", label: "Items (CRUD mẫu)" },
  { href: "pages/cart.html", label: "Giỏ hàng" },
];

// Hàm đếm tổng số lượng sản phẩm trong giỏ
function getCartCount() {
  const cart = JSON.parse(localStorage.getItem("cart") || "[]");
  return cart.reduce((total, item) => total + item.quantity, 0);
}

// Hàm cập nhật badge trên header
window.updateCartBadge = function() {
  const badge = document.getElementById("cart-badge");
  if (badge) {
    const count = getCartCount();
    badge.textContent = count;
    badge.style.display = count > 0 ? "inline-block" : "none";
  }
};

function renderLayout() {
  const root = document.body.dataset.root || "./";
  const currentPath = window.location.pathname;

  const links = MENU.map((item) => {
    const isActive = currentPath.endsWith("/" + item.href) ||
      (item.href === "index.html" && currentPath.endsWith("/"));
    
    // Thêm badge cho riêng mục Giỏ hàng
    let badgeHtml = "";
    if (item.href === "pages/cart.html") {
      badgeHtml = `<span id="cart-badge" class="cart-badge" style="display:none;">0</span>`;
    }

    return `<a href="${root}${item.href}" class="${isActive ? "active" : ""}">
      ${item.label} ${badgeHtml}
    </a>`;
  }).join("");

  document.getElementById("app-header").innerHTML = `
    <div class="container header-inner">
      <a href="${root}index.html" class="brand">
        <img src="${root}assets/images/logo.svg" alt="logo" width="28" height="28">
        <span>${CONFIG.APP_NAME}</span>
      </a>
      <nav class="nav">${links}</nav>
    </div>`;

  document.getElementById("app-footer").innerHTML = `
    <div class="container">© ${new Date().getFullYear()} HN-KS25-CNTT1 · Base code thực tập doanh nghiệp</div>`;

  // Cập nhật số lượng giỏ hàng ngay sau khi render header
  window.updateCartBadge();
}

renderLayout();