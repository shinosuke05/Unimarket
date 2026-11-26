
const MENU = [
  {
    href: "index.html",
    label: "Trang chủ"
  },
  {
    href: "pages/products.html",
    label: "Sản phẩm"
  },
  {
    href: "pages/items.html",
    label: "Items"
  },
  {
    href: "pages/cart.html",
    label: "Giỏ hàng"
  },
  {
    href: "pages/auth.html",
    label: "Đăng nhập / Đăng ký"
  },
  {
    href: "pages/profile.html",
    label: "Hồ sơ"
  },
  {
    href: "pages/address.html",
    label: "Sổ địa chỉ"
  },
];

let cartBadgeRequest = 0;

// Lấy số lượng giỏ hàng từ Backend.
async function getCartCount() {
  if (!localStorage.getItem("token")) {
    return 0;
  }

  const cart = await api.get("/cart");

  return (cart.items || []).reduce(
    (total, item) =>
      total + Math.max(0, Number(item.quantity) || 0),
    0
  );
}

// Cập nhật số lượng trên header.
window.updateCartBadge = async function () {
  const badge = document.getElementById("cart-badge");

  if (!badge) return;

  const requestId = ++cartBadgeRequest;

  try {
    const count = await getCartCount();

    if (requestId !== cartBadgeRequest) return;

    badge.textContent = count;

    badge.style.display =
      count > 0 ? "inline-block" : "none";

  } catch (error) {
    if (requestId !== cartBadgeRequest) return;

    badge.textContent = "0";
    badge.style.display = "none";

    console.warn(
      "Không thể tải số lượng giỏ hàng:",
      error.message
    );
  }
};

function renderLayout() {
  const root = document.body.dataset.root || "./";
  const currentPath = window.location.pathname;

  const hasToken = Boolean(
    localStorage.getItem("token")
  );

  const links = MENU.map((item) => {
    const isActive =
      currentPath.endsWith("/" + item.href) ||
      (
        item.href === "index.html" &&
        currentPath.endsWith("/")
      );

    let badgeHtml = "";

    if (item.href === "pages/cart.html") {
      badgeHtml = `
        <span
          id="cart-badge"
          class="cart-badge"
          style="display:none;"
        >0</span>
      `;
    }

    return `
      <a
        href="${root}${item.href}"
        class="${isActive ? "active" : ""}"
      >
        ${item.label}
        ${badgeHtml}
      </a>
    `;
  }).join("");

  const logoutHtml = hasToken
    ? `
      <button
        id="btn-logout"
        type="button"
        class="btn btn-small btn-danger"
      >
        Đăng xuất
      </button>
    `
    : "";

  const header = document.getElementById("app-header");

  if (header) {
    header.innerHTML = `
      <div class="container header-inner">

        <a href="${root}index.html" class="brand">

          <img
            src="${root}assets/images/logo.svg"
            alt="logo"
            width="28"
            height="28"
          >

          <span>${CONFIG.APP_NAME}</span>

        </a>

        <nav class="nav">
          ${links}
          ${logoutHtml}
        </nav>

      </div>
    `;
  }

  const footer = document.getElementById("app-footer");

  if (footer) {
    footer.innerHTML = `
      <div class="container">
        © ${new Date().getFullYear()}
        HN-KS25-CNTT1 · Base code thực tập doanh nghiệp
      </div>
    `;
  }

  const btnLogout = document.getElementById("btn-logout");

  if (btnLogout) {
    btnLogout.addEventListener("click", () => {
      localStorage.removeItem("token");
      sessionStorage.removeItem("unimarket_user_id");

      window.location.href =
        `${root}pages/auth.html`;
    });
  }

  window.updateCartBadge();
}

renderLayout();
