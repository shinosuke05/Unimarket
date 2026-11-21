
const productGrid = document.getElementById("products-grid");
const productMessage = document.getElementById("products-message");
const productCount = document.getElementById("products-count");
const pagination = document.getElementById("products-pagination");

const filterForm = document.getElementById("product-filter-form");
const searchForm = document.getElementById("product-search-form");
const searchInput = document.getElementById("product-search");
const categorySelect = document.getElementById("filter-category");
const minPriceInput = document.getElementById("filter-min-price");
const maxPriceInput = document.getElementById("filter-max-price");
const conditionSelect = document.getElementById("filter-condition");
const inStockInput = document.getElementById("filter-in-stock");
const sortSelect = document.getElementById("product-sort");

const PAGE_LIMIT = 12;
const SORT_OPTIONS = ["newest", "price_asc", "price_desc"];

function getProductParams() {
  const url = new URLSearchParams(window.location.search);
  const page = Number(url.get("page"));

  return {
    page: Number.isInteger(page) && page > 0 ? page : 1,
    limit: PAGE_LIMIT,
    q: url.get("q") || "",
    category_id: url.get("category_id") || "",
    min_price: url.get("min_price") || "",
    max_price: url.get("max_price") || "",
    item_condition: url.get("item_condition") || "",
    in_stock: url.get("in_stock") || "",
    sort: SORT_OPTIONS.includes(url.get("sort"))
      ? url.get("sort")
      : "newest"
  };
}

function updateProductUrl(changes) {
  const params = new URLSearchParams(window.location.search);

  Object.entries(changes).forEach(([key, value]) => {
    if (value === "" || value === null || value === undefined) {
      params.delete(key);
    } else {
      params.set(key, String(value));
    }
  });

  const query = params.toString();
  const nextUrl = window.location.pathname + (query ? `?${query}` : "");

  window.history.pushState({}, "", nextUrl);
  syncProductFilters();
  loadProducts();
}

function syncProductFilters() {
  const params = getProductParams();

  searchInput.value = params.q;
  categorySelect.value = params.category_id;
  minPriceInput.value = params.min_price;
  maxPriceInput.value = params.max_price;
  conditionSelect.value = params.item_condition;
  inStockInput.checked = params.in_stock === "true";
  sortSelect.value = params.sort;
}

function escapeProductHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[char]);
}

function formatProductPrice(price) {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND"
  }).format(Number(price) || 0);
}

function renderProductCard(product) {
  const images = Array.isArray(product.images) ? product.images : [];
  const primaryImage = images.find((image) => image.is_primary);
  const imageUrl = primaryImage?.image_url || images[0]?.image_url;

  const imageHtml = imageUrl
    ? `<img src="${escapeProductHtml(imageUrl)}"
         alt="${escapeProductHtml(product.name)}" loading="lazy">`
    : `<div class="products-no-image">Chưa có ảnh</div>`;

  const condition = product.item_condition
    ? `<span class="products-condition">
         Tình trạng: ${escapeProductHtml(product.item_condition)}
       </span>`
    : "";

  return `
    <article class="products-card">
      <div class="products-card-image">${imageHtml}</div>
      <div class="products-card-info">
        <h3>${escapeProductHtml(product.name)}</h3>
        ${condition}
        <p class="products-card-price">${formatProductPrice(product.price)}</p>
      </div>
    </article>
  `;
}

async function loadProductCategories() {
  try {
    const categories = await api.get("/categories");

    categorySelect.innerHTML =
      '<option value="">Tất cả danh mục</option>';

    categories.forEach((category) => {
      const option = document.createElement("option");
      option.value = String(category.id);
      option.textContent = category.name;
      categorySelect.appendChild(option);
    });

    syncProductFilters();
  } catch (error) {
    console.error("Không tải được danh mục:", error);
    productMessage.textContent =
      "Không tải được danh mục. Bạn vẫn có thể tìm kiếm sản phẩm.";
  }
}

let productRequestId = 0;

async function loadProducts() {
  const requestId = ++productRequestId;
  const params = getProductParams();

  productMessage.textContent = "Đang tải sản phẩm...";
  productGrid.innerHTML = "";
  productCount.textContent = "";
  pagination.innerHTML = "";

  const apiParams = {
    page: params.page,
    limit: params.limit,
    sort: params.sort
  };

  if (params.q.trim()) apiParams.q = params.q.trim();
  if (params.category_id) apiParams.category_id = params.category_id;
  if (params.min_price) apiParams.min_price = params.min_price;
  if (params.max_price) apiParams.max_price = params.max_price;
  if (params.item_condition) {
    apiParams.item_condition = params.item_condition;
  }
  if (params.in_stock === "true") apiParams.in_stock = true;

  try {
    const result = await api.get("/products", apiParams);
    if (requestId !== productRequestId) return;

    const products = result.products || [];
    const total = Number(result.total) || 0;
    const totalPages = Number(result.total_pages) || 0;

    productMessage.textContent = "";

    if (!products.length) {
      productMessage.textContent = "Không tìm thấy sản phẩm phù hợp.";
      return;
    }

    productCount.textContent = `Tìm thấy ${total} sản phẩm`;
    productGrid.innerHTML = products.map(renderProductCard).join("");

    renderProductPagination(params.page, totalPages);
  } catch (error) {
    if (requestId !== productRequestId) return;
    console.error("Lỗi tải sản phẩm:", error);
    productMessage.textContent =
      error.message || "Không thể tải sản phẩm. Vui lòng thử lại.";
  }
}

function renderProductPagination(currentPage, totalPages) {
  pagination.innerHTML = "";

  if (totalPages <= 1) return;

  function addPageButton(label, page, disabled = false, active = false) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.disabled = disabled;
    button.className = active ? "products-page-active" : "";

    if (active) button.setAttribute("aria-current", "page");

    button.addEventListener("click", () => {
      updateProductUrl({ page });
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    pagination.appendChild(button);
  }

  addPageButton("Trước", currentPage - 1, currentPage <= 1);

  for (let page = 1; page <= totalPages; page++) {
    addPageButton(String(page), page, false, page === currentPage);
  }

  addPageButton("Sau", currentPage + 1, currentPage >= totalPages);
}

// Tìm kiếm theo tên
searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  updateProductUrl({
    q: searchInput.value.trim(),
    page: 1
  });
});

// Áp dụng bộ lọc
filterForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const minPrice = minPriceInput.value;
  const maxPrice = maxPriceInput.value;

  if (
    minPrice !== "" &&
    maxPrice !== "" &&
    Number(minPrice) > Number(maxPrice)
  ) {
    productMessage.textContent =
      "Giá tối thiểu không được lớn hơn giá tối đa.";
    return;
  }

  updateProductUrl({
    category_id: categorySelect.value,
    min_price: minPrice,
    max_price: maxPrice,
    item_condition: conditionSelect.value,
    in_stock: inStockInput.checked ? "true" : "",
    page: 1
  });
});

// Sắp xếp sản phẩm
sortSelect.addEventListener("change", () => {
  updateProductUrl({
    sort: sortSelect.value,
    page: 1
  });
});

// Xóa tất cả điều kiện lọc
document.getElementById("reset-filters").addEventListener("click", () => {
  window.history.pushState({}, "", window.location.pathname);
  syncProductFilters();
  loadProducts();
});

// Khôi phục khi người dùng bấm Back / Forward
window.addEventListener("popstate", () => {
  syncProductFilters();
  loadProducts();
});

// Khởi tạo trang
syncProductFilters();
loadProductCategories();
loadProducts();
