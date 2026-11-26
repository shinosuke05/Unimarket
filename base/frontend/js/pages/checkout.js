
"use strict";

const checkoutState = {
    items: [],
    addresses: [],
    buyNow: false,
    loading: false,
    ready: false
};

const checkoutEl = id => document.getElementById(id);

// Đồng bộ với DEFAULT_SHIPPING_FEE của Backend.
const SHIPPING_FEE = 0;

function checkoutError(message = "") {
    checkoutEl("checkout-error").textContent = message;
}

// ==================== ĐỊA CHỈ ====================

async function loadAddresses() {
    const addresses = await api.get("/addresses");

    checkoutState.addresses = addresses || [];

    const select = checkoutEl("address-select");

    select.replaceChildren(
        new Option("-- Chọn địa chỉ --", "")
    );

    checkoutState.addresses.forEach(address => {
        const label =
            `${address.recipient_name} - ` +
            `${address.street_address} - ` +
            `${address.phone}`;

        select.add(
            new Option(label, String(address.id))
        );
    });

    const defaultAddress =
        checkoutState.addresses.find(
            address => address.is_default
        ) || checkoutState.addresses[0];

    if (defaultAddress) {
        select.value = String(defaultAddress.id);
        fillAddress();
    }
}

function fillAddress() {
    const addressId = Number(
        checkoutEl("address-select").value
    );

    const address = checkoutState.addresses.find(
        item => Number(item.id) === addressId
    );

    if (!address) return;

    checkoutEl("receiver-name").value =
        address.recipient_name || "";

    checkoutEl("receiver-phone").value =
        address.phone || "";
}

// ==================== SẢN PHẨM ====================

async function loadCheckoutItems() {
    const params = new URLSearchParams(
        window.location.search
    );

    checkoutState.buyNow =
        params.get("mode") === "buy-now";

    if (checkoutState.buyNow) {
        const itemId = Number(params.get("item_id"));
        const quantity = Number(
            params.get("quantity") || 1
        );

        if (
            !Number.isSafeInteger(itemId) ||
            itemId < 1 ||
            !Number.isSafeInteger(quantity) ||
            quantity < 1 ||
            quantity > 999
        ) {
            throw new Error(
                "Thông tin sản phẩm không hợp lệ."
            );
        }

        const item = await api.get(`/items/${itemId}`);

        if (
            item.status !== "AVAILABLE" ||
            Number(item.quantity) < quantity
        ) {
            throw new Error(
                "Sản phẩm không còn đủ số lượng."
            );
        }

        checkoutState.items = [{
            product_id: item.id,
            product_name: item.name,
            price: Number(item.price),
            quantity
        }];

    } else {
        const cart = await api.get("/cart");

        checkoutState.items = cart.items || [];
    }
}

// ==================== TÓM TẮT ====================

function renderSummary() {
    const container = checkoutEl(
        "checkout-summary-items"
    );

    const items = checkoutState.items;

    if (!items.length) {
        container.innerHTML = `
            <p class="muted">
                Giỏ hàng đang trống.
                <a href="cart.html">Về giỏ hàng</a>
            </p>
        `;

        checkoutEl("checkout-submit").disabled = true;
        return;
    }

    let subtotal = 0;

    let html = items.map(item => {
        const total =
            Number(item.price) * Number(item.quantity);

        subtotal += total;

        return `
            <div class="summary-item">

                <span>
                    ${escapeHtml(item.product_name)}
                    x${Number(item.quantity)}
                </span>

                <span>${formatMoney(total)}</span>

            </div>
        `;
    }).join("");

    const shipping = document.querySelector(
        'input[name="shipping"]:checked'
    ).value;

    const shippingFee =
        shipping === "delivery" ? SHIPPING_FEE : 0;

    html += `
        <div class="summary-item"
             style="margin-top:16px;">

            <span>Tạm tính</span>
            <span>${formatMoney(subtotal)}</span>

        </div>

        <div class="summary-item">

            <span>Phí vận chuyển</span>
            <span>${formatMoney(shippingFee)}</span>

        </div>

        <div class="summary-total">

            <span>Tổng cộng</span>

            <span class="text-primary">
                ${formatMoney(subtotal + shippingFee)}
            </span>

        </div>
    `;

    container.innerHTML = html;
}

function updateShipping() {
    const shipping = document.querySelector(
        'input[name="shipping"]:checked'
    ).value;

    const isDelivery = shipping === "delivery";

    checkoutEl("shipping-address-group").hidden =
        !isDelivery;

    checkoutEl("address-select").required =
        isDelivery;

    renderSummary();
}

// ==================== ĐẶT HÀNG ====================

async function handleCheckout(event) {
    event.preventDefault();

    if (
        checkoutState.loading ||
        !checkoutState.ready ||
        !checkoutState.items.length
    ) return;

    checkoutError();

    const shipping = document.querySelector(
        'input[name="shipping"]:checked'
    ).value;

    const payment = document.querySelector(
        'input[name="payment"]:checked'
    ).value;

    const receiverName =
        checkoutEl("receiver-name").value.trim();

    const receiverPhone =
        checkoutEl("receiver-phone").value.trim();

    if (
        receiverName.length < 2 ||
        receiverPhone.length < 8
    ) {
        checkoutError(
            "Vui lòng nhập đầy đủ thông tin người nhận."
        );
        return;
    }

    let shippingAddress = null;

    if (shipping === "delivery") {
        const addressId = Number(
            checkoutEl("address-select").value
        );

        const address = checkoutState.addresses.find(
            item => Number(item.id) === addressId
        );

        if (!address) {
            checkoutError(
                "Vui lòng chọn địa chỉ nhận hàng."
            );
            return;
        }

        shippingAddress = address.street_address;
    }

    const data = {
        receiver_name: receiverName,
        receiver_phone: receiverPhone,

        fulfillment_type:
            shipping === "delivery"
                ? "DELIVERY"
                : "PICKUP",

        payment_method:
            payment === "cod"
                ? "COD"
                : "BANK_TRANSFER",

        shipping_address: shippingAddress,

        note:
            checkoutEl("order-note").value.trim()
            || null
    };

    const button = checkoutEl("checkout-submit");

    checkoutState.loading = true;
    button.disabled = true;
    button.textContent = "Đang xử lý...";

    let submitted = false;

    try {
        let order;

        if (checkoutState.buyNow) {
            data.items = checkoutState.items.map(
                item => ({
                    item_id: Number(item.product_id),
                    quantity: Number(item.quantity)
                })
            );

            order = await api.post(
                "/orders/buy-now",
                data
            );

        } else {
            order = await api.post(
                "/orders/checkout",
                data
            );
        }

        submitted = true;

        if (!order || !order.id) {
            throw new Error(
                "Không nhận được mã đơn hàng. " +
                "Hãy kiểm tra lịch sử đơn hàng."
            );
        }

        window.location.href =
            `order-result.html?orderId=${encodeURIComponent(order.id)}`;

    } catch (error) {
        if (submitted || error.status === 0 ||
            error.status >= 500) {
            checkoutError(
                "Chưa xác định được kết quả đặt hàng. " +
                "Hãy kiểm tra lịch sử đơn hàng trước khi thử lại."
            );

            checkoutState.ready = false;
        } else {
            checkoutError(
                error.message || "Không thể đặt hàng."
            );
        }
    } finally {
        checkoutState.loading = false;

        button.disabled = !checkoutState.ready;

        button.textContent = "Xác nhận Đặt hàng";
    }
}

// ==================== KHỞI TẠO ====================

async function initCheckout() {
    if (!localStorage.getItem("token")) {
        window.location.href = "auth.html";
        return;
    }

    checkoutEl("checkout-form").addEventListener(
        "submit",
        handleCheckout
    );

    checkoutEl("address-select").addEventListener(
        "change",
        fillAddress
    );

    document.querySelectorAll(
        'input[name="shipping"]'
    ).forEach(input => {
        input.addEventListener(
            "change",
            updateShipping
        );
    });

    try {
        await Promise.all([
            loadAddresses(),
            loadCheckoutItems()
        ]);

        checkoutState.ready =
            checkoutState.items.length > 0;

        updateShipping();

        checkoutEl("checkout-submit").disabled =
            !checkoutState.ready;

    } catch (error) {
        checkoutError(error.message);

        checkoutEl("checkout-summary-items").textContent =
            "Không thể tải thông tin đơn hàng.";

        checkoutEl("checkout-submit").disabled = true;
    }
}

document.addEventListener(
    "DOMContentLoaded",
    initCheckout
);
