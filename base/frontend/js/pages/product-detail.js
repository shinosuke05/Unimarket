
"use strict";

const detailState = {
  product: null,
  loadingCart: false,
};

const detailEl = (id) => document.getElementById(id);

function detailEscape(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);
}

function detailPrice(value) {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(Number(value) || 0);
}

function detailImageUrl(value) {
  if (typeof value !== "string") return "../assets/images/logo.svg";
  const url = value.trim();
  if (!url) return "../assets/images/logo.svg";

  // Chỉ sử dụng URL ảnh an toàn.
  if (/^https?:\/\//i.test(url)) return url;
  if (url.startsWith("/") && !url.startsWith("//")) return url;
  if (/^(?:\.\.\/|\.\/|assets\/)/.test(url)) return url;

  return "../assets/images/logo.svg";
}

function detailAvailable(product) {
  return product.status === "available" && Number(product.stock) > 0;
}

function detailMessage(message, isError = false) {
  const element = detailEl("product-action-message");
  element.textContent = message;
  element.style.color = isError ? "#dc2626" : "#15803d";
}

function detailSetMainImage(url, alt) {
  const image = detailEl("product-main-image");
  image.src = detailImageUrl(url);
  image.alt = alt;
}

function detailRenderGallery(product) {
  const images = [...(product.images || [])].sort(
    (a, b) => Number(a.sort_order || 0) - Number(b.sort_order || 0)
  );

  const primary = images.find((image) => image.is_primary) || images[0];
  detailSetMainImage(primary?.image_url, product.name);

  const thumbnails = detailEl("product-thumbnails");
  thumbnails.replaceChildren();

  images.forEach((image, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "product-gallery-thumb";
    button.setAttribute("aria-label", `Xem ảnh ${index + 1}`);

    const img = document.createElement("img");
    img.src = detailImageUrl(image.image_url);
    img.alt = `${product.name} - ảnh ${index + 1}`;

    button.appendChild(img);
    button.addEventListener("click", () => {
      detailSetMainImage(image.image_url, img.alt);
      thumbnails.querySelectorAll("button").forEach((item) => {
        item.classList.remove("active");
      });
      button.classList.add("active");
    });

    if (image === primary) button.classList.add("active");
    thumbnails.appendChild(button);
  });
}

function detailRenderProduct(product) {
  detailState.product = product;

  document.title = `${product.name} | UniMarket`;
  detailEl("breadcrumb-product-name").textContent = product.name;
  detailEl("product-detail-name").textContent = product.name;
  detailEl("product-detail-price").textContent = detailPrice(product.price);
  detailEl("product-detail-condition").textContent =
    product.item_condition || "Chưa cập nhật";
  detailEl("product-detail-stock").textContent =
    `${product.stock} sản phẩm`;
  detailEl("product-detail-status").textContent =
    detailAvailable(product) ? "Còn hàng" : "Hết hàng";
  detailEl("product-detail-description").textContent =
    product.description || "Sản phẩm chưa có mô tả.";

  const quantity = detailEl("product-quantity-input");
  quantity.value = 1;
  quantity.max = Math.max(1, Number(product.stock) || 1);
  quantity.disabled = !detailAvailable(product);

  detailEl("product-add-cart").disabled = !detailAvailable(product);
  detailEl("product-buy-now").disabled = !detailAvailable(product);

  detailRenderGallery(product);

  detailEl("product-detail-message").hidden = true;
  detailEl("product-detail-content").hidden = false;
}

async function detailFindProduct(id) {
  // Ưu tiên API chi tiết khi Backend có endpoint /products/{id}.
  try {
    return await api.get(`/products/${id}`);
  } catch (error) {
    if (error.status !== 404) throw error;
  }

  // Fallback để kiểm thử UI trên nhánh chưa có API chi tiết.
  // Có giới hạn 100 sản phẩm mỗi trang theo Backend hiện tại.
  let page = 1;

  while (true) {
    const result = await api.get("/products", { page, limit: 100 });
    const product = (result.products || []).find(
      (item) => Number(item.id) === id
    );

    if (product) return product;
    if (page >= Number(result.total_pages || 0)) break;
    page += 1;
  }

  throw new Error("Không tìm thấy sản phẩm.");
}

function detailRenderRelated(products) {
  const grid = detailEl("product-related-grid");
  grid.replaceChildren();

  if (!products.length) {
    detailEl("product-related-message").textContent =
      "Chưa có sản phẩm liên quan.";
    return;
  }

  detailEl("product-related-message").textContent = "";

  products.forEach((product) => {
    const image = product.images?.find((item) => item.is_primary)
      || product.images?.[0];

    const card = document.createElement("a");
    card.className = "product-related-card";
    card.href = `product-detail.html?id=${encodeURIComponent(product.id)}`;

    const img = document.createElement("img");
    img.src = detailImageUrl(image?.image_url);
    img.alt = product.name;
    img.loading = "lazy";

    const name = document.createElement("h3");
    name.textContent = product.name;

    const condition = document.createElement("span");
    condition.textContent = `Tình trạng: ${product.item_condition}`;

    const price = document.createElement("strong");
    price.textContent = detailPrice(product.price);

    card.append(img, name, condition, price);
    grid.appendChild(card);
  });
}


async function detailLoadRelated(product) {
  detailShowRelatedState(
    "loading",
    "Đang tải sản phẩm liên quan..."
  );

  try {
    const related = [];
    let page = 1;

    while (related.length < 4) {
      const result = await api.get("/products", {
        page,
        limit: 100
      });

      const matches = (result.products || []).filter(
        (item) =>
          Number(item.id) !== Number(product.id) &&
          Number(item.category_id) === Number(product.category_id) &&
          item.is_visible !== false
      );

      related.push(...matches);

      if (page >= Number(result.total_pages || 0)) break;
      page += 1;
    }

    if (related.length === 0) {
      detailShowRelatedState(
        "empty",
        "Hiện chưa có sản phẩm liên quan."
      );
      return;
    }

    detailRenderRelated(related.slice(0, 4));

  } catch (error) {
    console.error("Lỗi tải sản phẩm liên quan:", error);

    detailShowRelatedState(
      "error",
      "Không thể tải sản phẩm liên quan.",
      () => detailLoadRelated(product)
    );
  }
}


function detailGetQuantity() {
  const product = detailState.product;
  const quantity = Number(detailEl("product-quantity-input").value);

  if (
    !Number.isInteger(quantity) ||
    quantity < 1 ||
    quantity > Number(product.stock)
  ) {
    detailMessage(
      `Số lượng phải từ 1 đến ${product.stock}.`,
      true
    );
    return null;
  }

  return quantity;
}

function detailGetUserId() {
  // Chỉ dùng ID từ trạng thái đăng nhập thực tế khi được tích hợp.
  // Không tự gán user_id=1 vì có thể thêm vào giỏ của người khác.
  const stored = sessionStorage.getItem("unimarket_user_id");
  const id = Number(stored);
  return stored && Number.isSafeInteger(id) && id > 0 ? id : null;
}

async function detailAddToCart(buyNow = false) {
  if (detailState.loadingCart || !detailState.product) return;

  const product = detailState.product;
  if (!detailAvailable(product)) {
    detailMessage("Sản phẩm đã hết hàng.", true);
    return;
  }

  const quantity = detailGetQuantity();
  if (quantity === null) return;

  const userId = detailGetUserId();

  if (!userId) {
    detailMessage(
      "Bạn cần đăng nhập để thêm sản phẩm vào giỏ hàng.",
      true
    );
    return;
  }

  detailState.loadingCart = true;
  detailEl("product-add-cart").disabled = true;
  detailEl("product-buy-now").disabled = true;

  try {
    await api.post(
      `/cart/items?user_id=${encodeURIComponent(userId)}`,
      { product_id: product.id, quantity }
    );

    detailMessage("Đã thêm sản phẩm vào giỏ hàng.");

    if (buyNow) {
      // Chỉ chuyển sang giỏ hàng khi trang giỏ hàng đã tồn tại.
      detailMessage(
        "Đã thêm vào giỏ. Tiếp tục thanh toán tại trang giỏ hàng."
      );
    }
  } catch (error) {
    detailMessage(
      error.message || "Không thể thêm sản phẩm vào giỏ.",
      true
    );
  } finally {
    detailState.loadingCart = false;
    detailEl("product-add-cart").disabled = !detailAvailable(product);
    detailEl("product-buy-now").disabled = !detailAvailable(product);
  }
}


function detailShowState(type, message, retry = null) {
  const box = detailEl("product-detail-message");

  detailEl("product-detail-content").hidden = true;
  box.hidden = false;

  const icons = {
    empty: "📦",
    error: "⚠️"
  };

  if (type === "loading") {
    box.innerHTML = `
      <div class="ui-state ui-loading" role="status">
        <span class="ui-spinner" aria-hidden="true"></span>
        <span>${detailEscape(message)}</span>
      </div>
    `;
    return;
  }

  box.innerHTML = `
    <div class="ui-state ui-${type}"
         role="${type === "error" ? "alert" : "status"}">
      <span class="ui-state-icon" aria-hidden="true">
        ${icons[type] || "📦"}
      </span>
      <strong>
        ${type === "error" ? "Không thể tải sản phẩm" : "Không tìm thấy sản phẩm"}
      </strong>
      <span>${detailEscape(message)}</span>
      ${retry ? `
        <button type="button" class="btn btn-primary detail-retry-btn">
          Thử lại
        </button>
      ` : ""}
    </div>
  `;

  if (retry) {
    box.querySelector(".detail-retry-btn")
      .addEventListener("click", retry);
  }
}

function detailShowRelatedState(type, message, retry = null) {
  const box = detailEl("product-related-message");
  const grid = detailEl("product-related-grid");

  grid.replaceChildren();

  if (type === "loading") {
    box.innerHTML = `
      <div class="ui-state ui-loading" role="status">
        <span class="ui-spinner" aria-hidden="true"></span>
        <span>${detailEscape(message)}</span>
      </div>
    `;
    return;
  }

  box.innerHTML = `
    <div class="ui-state ui-${type}"
         role="${type === "error" ? "alert" : "status"}">
      <span>${detailEscape(message)}</span>
      ${retry ? `
        <button type="button" class="btn btn-primary detail-retry-btn">
          Thử lại
        </button>
      ` : ""}
    </div>
  `;

  if (retry) {
    box.querySelector(".detail-retry-btn")
      .addEventListener("click", retry);
  }
}



async function detailInit() {
  const id = Number(
    new URLSearchParams(location.search).get("id")
  );

  detailState.product = null;

  if (!Number.isSafeInteger(id) || id < 1) {
    detailShowState(
      "empty",
      "Đường dẫn sản phẩm không hợp lệ."
    );
    return;
  }

  detailShowState("loading", "Đang tải thông tin sản phẩm...");

  try {
    const product = await detailFindProduct(id);

    if (!product || product.is_visible === false) {
      detailShowState(
        "empty",
        "Sản phẩm không tồn tại hoặc đã ngừng hiển thị."
      );
      return;
    }

    detailRenderProduct(product);
    detailLoadRelated(product);

  } catch (error) {
    console.error("Lỗi tải chi tiết sản phẩm:", error);

    if (error.message === "Không tìm thấy sản phẩm.") {
      detailShowState(
        "empty",
        "Không tìm thấy sản phẩm bạn yêu cầu."
      );
      return;
    }

    detailShowState(
      "error",
      "Không thể tải thông tin sản phẩm. Vui lòng thử lại.",
      detailInit
    );
  }
}


detailEl("product-add-cart").addEventListener("click", () => {
  detailAddToCart(false);
});

detailEl("product-buy-now").addEventListener("click", () => {
  detailAddToCart(true);
});

const contactLinks = {
  facebook: "", // Điền link Facebook chính thức
  zalo: "",     // Điền link Zalo chính thức
};

function setupContactLink(id, url) {
  const link = document.getElementById(id);
  if (!link) return;

  if (url) {
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  } else {
    link.removeAttribute("href");
    link.setAttribute("aria-disabled", "true");
    link.title = "Kênh liên hệ đang được cập nhật";
  }
}

setupContactLink("product-contact-facebook", contactLinks.facebook);
setupContactLink("product-contact-zalo", contactLinks.zalo);

detailInit();

const quantityInput = document.getElementById("product-quantity-input");
const quantityMinus = document.getElementById("quantity-minus");
const quantityPlus = document.getElementById("quantity-plus");

quantityMinus.addEventListener("click", () => {
  if (quantityInput.disabled || !detailState.product) return;

  const current = Number(quantityInput.value) || 1;
  quantityInput.value = Math.max(1, current - 1);
});

quantityPlus.addEventListener("click", () => {
  if (quantityInput.disabled || !detailState.product) return;

  const current = Number(quantityInput.value) || 1;
  const maxStock = Number(detailState.product.stock) || 1;

  quantityInput.value = Math.min(maxStock, current + 1);
});

quantityInput.addEventListener("change", () => {
  if (quantityInput.disabled || !detailState.product) return;

  const maxStock = Number(detailState.product.stock) || 1;
  const value = Number(quantityInput.value);

  quantityInput.value = Number.isFinite(value)
    ? Math.max(1, Math.min(maxStock, Math.floor(value)))
    : 1;
});
