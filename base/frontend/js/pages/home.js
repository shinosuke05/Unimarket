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
  const detailUrl = `pages/product-detail.html?id=${encodeURIComponent(product.id)}`;
  return `
    <a href="${detailUrl}" class="home-product-link">
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
</a>
  `;
}

// Lấy sản phẩm mới nhất từ API
async function loadLatestProducts() {
  const container = document.getElementById("latest-product-list");

  if (!container) return;

  container.innerHTML = '<p class="muted">Đang tải sản phẩm...</p>';

  try {
    const result = await api.get("/products", {
      page: 1,
      limit: 8,
      sort: "newest"
    });

    const products = result.products || [];

    if (products.length === 0) {
      container.innerHTML =
        '<p class="muted">Hiện chưa có sản phẩm nào.</p>';
      return;
    }

    container.innerHTML = products
      .map(renderHomeProduct)
      .join("");

  } catch (error) {
    console.error("Lỗi tải sản phẩm mới:", error);

    container.textContent =
      "Không tải được sản phẩm. Vui lòng thử lại sau.";
  }
}

// Danh mục: chờ API danh mục từ Backend
async function loadHomeCategories() {
  const container = document.getElementById("category-list");
  if (!container) return;

  container.innerHTML = '<p class="muted">Đang tải danh mục...</p>';

  try {
    const categories = await api.get("/categories");

    if (!categories.length) {
      container.innerHTML =
        '<p class="muted">Chưa có danh mục sản phẩm.</p>';
      return;
    }

    container.innerHTML = categories.map(category => `
      <a href="pages/products.html?category_id=${encodeURIComponent(category.id)}"
         class="home-category-card">
        <h3>${escapeHomeHtml(category.name)}</h3>
        <p>${escapeHomeHtml(category.description || "")}</p>
      </a>
    `).join("");

  } catch (error) {
    console.error("Lỗi tải danh mục:", error);
    container.textContent = "Không tải được danh mục sản phẩm.";
  }
}

// Sản phẩm nổi bật: chờ tiêu chí và API từ Backend

async function loadFeaturedProducts() {
  const container = document.getElementById("featured-product-list");
  if (!container) return;

  container.innerHTML =
    '<p class="muted">Đang tải sản phẩm nổi bật...</p>';

  try {
    const result = await api.get("/products", {
      page: 1,
      limit: 8,
      sort: "price_desc"
    });

    const products = result.products || [];

    if (products.length === 0) {
      container.innerHTML =
        '<p class="muted">Chưa có sản phẩm nổi bật.</p>';
      return;
    }

    container.innerHTML = products.map(renderHomeProduct).join("");

  } catch (error) {
    console.error("Lỗi tải sản phẩm nổi bật:", error);
    container.textContent =
      "Không tải được sản phẩm nổi bật.";
  }
}


// Khởi tạo trang chủ
function initHomePage() {
  loadHomeCategories();
  loadLatestProducts();
  loadFeaturedProducts();
}

initHomePage();
