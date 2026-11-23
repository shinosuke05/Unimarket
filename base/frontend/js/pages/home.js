// Trang chủ: gọi GET /api/health (qua axios trong js/api.js) để kiểm tra FE -> BE -> MySQL đã thông chưa.

// async function checkHealth() {
//   const box = document.getElementById("health-status");
//   box.className = "status status-loading";
//   box.textContent = "Đang kiểm tra kết nối...";

//   try {
//     const result = await api.get("/health");
//     box.className = "status status-ok";
//     box.textContent = `✅ Backend OK · MySQL: ${result.database}`;
//   } catch (error) {
//     box.className = "status status-error";
//     // 503 = backend chạy nhưng không nối được MySQL; 0 = không gọi được backend
//     box.textContent = `❌ ${error.status === 503 ? "Backend chạy nhưng MySQL lỗi: " + error.data.detail : error.message}`;
//   }
// }

// document.getElementById("api-url").textContent = CONFIG.API_BASE_URL;
// document.getElementById("btn-recheck").addEventListener("click", checkHealth);
// checkHealth();

// Chuyển giá sản phẩm thành định dạng tiền Việt Nam
function formatHomePrice(price) {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND"
  }).format(Number(price) || 0);
}

// Tránh đưa HTML không an toàn từ dữ liệu API vào trang
function escapeHomeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[char]);
}

// Tạo HTML cho một sản phẩm
function renderHomeProduct(product) {
  const primaryImage = product.images?.find(
    (image) => image.is_primary
  );

  const imageUrl = primaryImage?.image_url
    || product.images?.[0]?.image_url
    || "";

  const imageHtml = imageUrl
    ? `<img src="${escapeHomeHtml(imageUrl)}"
            alt="${escapeHomeHtml(product.name)}"
            loading="lazy">`
    : `<div class="home-no-image">Chưa có ảnh</div>`;

  const condition = product.item_condition
    ? `<span class="home-condition">
         Tình trạng: ${escapeHomeHtml(product.item_condition)}
       </span>`
    : "";

  return `
    <article class="home-product-card">
      <div class="home-product-image">
        ${imageHtml}
      </div>

      <div class="home-product-info">
        <h3>${escapeHomeHtml(product.name)}</h3>

        ${condition}

        <p class="home-product-price">
          ${formatHomePrice(product.price)}
        </p>
      </div>
    </article>
  `;
}


/* ===== T3C6383: LOADING / EMPTY / ERROR ===== */

// Hiển thị trạng thái đang tải
function homeShowLoading(container, message) {
  container.innerHTML = `
    <div class="ui-state ui-loading" role="status">
      <span class="ui-spinner" aria-hidden="true"></span>
      <span>${escapeHomeHtml(message)}</span>
    </div>
  `;
}

// Hiển thị trạng thái không có dữ liệu
function homeShowEmpty(container, message) {
  container.innerHTML = `
    <div class="ui-state ui-empty" role="status">
      <span class="ui-state-icon" aria-hidden="true">📦</span>
      <strong>Chưa có dữ liệu</strong>
      <span>${escapeHomeHtml(message)}</span>
    </div>
  `;
}

// Hiển thị lỗi và nút thử lại
function homeShowError(container, message, retryFunction) {
  container.innerHTML = `
    <div class="ui-state ui-error" role="alert">
      <span class="ui-state-icon" aria-hidden="true">⚠️</span>
      <strong>Không thể tải dữ liệu</strong>
      <span>${escapeHomeHtml(message)}</span>
      <button class="btn btn-primary home-retry-btn" type="button">
        Thử lại
      </button>
    </div>
  `;

  container
    .querySelector(".home-retry-btn")
    .addEventListener("click", retryFunction);
}

// Sản phẩm mới nhất
async function loadLatestProducts() {
  const container = document.getElementById("latest-product-list");
  if (!container) return;

  homeShowLoading(container, "Đang tải sản phẩm mới nhất...");

  try {
    const result = await api.get("/products", {
      page: 1,
      limit: 8,
      sort: "newest"
    });

    const products = Array.isArray(result.products)
      ? result.products
      : [];

    if (!products.length) {
      homeShowEmpty(container, "Hiện chưa có sản phẩm nào.");
      return;
    }

    container.innerHTML = products.map(renderHomeProduct).join("");
  } catch (error) {
    console.error("Lỗi tải sản phẩm mới:", error);
    homeShowError(
      container,
      "Không tải được sản phẩm mới nhất. Vui lòng thử lại.",
      loadLatestProducts
    );
  }
}

// Danh mục sản phẩm
async function loadHomeCategories() {
  const container = document.getElementById("category-list");
  if (!container) return;

  homeShowLoading(container, "Đang tải danh mục...");

  try {
    const result = await api.get("/categories");

    const categories = Array.isArray(result)
      ? result
      : Array.isArray(result.categories)
        ? result.categories
        : [];

    if (!categories.length) {
      homeShowEmpty(container, "Chưa có danh mục sản phẩm.");
      return;
    }

    container.innerHTML = categories.map((category) => `
      <a
        href="pages/products.html?category_id=${encodeURIComponent(category.id)}"
        class="home-category-card"
      >
        <h3>${escapeHomeHtml(category.name)}</h3>
        <p>${escapeHomeHtml(category.description || "")}</p>
      </a>
    `).join("");

  } catch (error) {
    console.error("Lỗi tải danh mục:", error);

    homeShowError(
      container,
      "Không thể tải danh mục sản phẩm. Vui lòng thử lại.",
      loadHomeCategories
    );
  }
}

// Sản phẩm nổi bật
async function loadFeaturedProducts() {
  const container = document.getElementById("featured-product-list");
  if (!container) return;

  homeShowLoading(container, "Đang tải sản phẩm nổi bật...");

  try {
    const result = await api.get("/products", {
      page: 1,
      limit: 8,
      sort: "price_desc"
    });

    const products = Array.isArray(result.products)
      ? result.products
      : [];

    if (!products.length) {
      homeShowEmpty(container, "Chưa có sản phẩm nổi bật.");
      return;
    }

    container.innerHTML = products.map(renderHomeProduct).join("");
  } catch (error) {
    console.error("Lỗi tải sản phẩm nổi bật:", error);

    homeShowError(
      container,
      "Không thể tải sản phẩm nổi bật. Vui lòng thử lại.",
      loadFeaturedProducts
    );
  }
}

// Khởi tạo trang chủ
function initHomePage() {
  loadHomeCategories();
  loadLatestProducts();
  loadFeaturedProducts();
}

initHomePage();


