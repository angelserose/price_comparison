// script.js — Updated for homepage to show all products from DB

// Load all products on homepage
window.onload = async () => {
    try {
        const response = await fetch('/all_products'); // fetch all products from backend
        const data = await response.json();
        displayProducts(data);
    } catch (err) {
        console.error(err);
        alert("Failed to load homepage products");
    }
};

// Display product cards (used both for homepage and search)
function displayProducts(data) {
    const container = document.getElementById("resultContainer");
    container.innerHTML = "";

    // Find cheapest per product
    const grouped = {};
    data.forEach(item => {
        if (!grouped[item.product]) grouped[item.product] = [];
        grouped[item.product].push(item);
    });

    for (const product in grouped) {
        const items = grouped[product];
        const minPrice = Math.min(...items.map(i => parseFloat(i.price)));

        items.forEach(item => {
            const card = document.createElement("div");
            card.className = "product-card";

            // IMAGE
            const img = document.createElement("img");
            img.src = item.image;
            img.className = "product-img";
            card.appendChild(img);

            // SALE BADGE (if on sale)
            if (item.is_on_sale && item.discount_percent) {
                const badge = document.createElement("span");
                badge.className = "sale-badge";
                badge.textContent = item.discount_percent + "% OFF";
                badge.style.position = "absolute";
                badge.style.top = "10px";
                badge.style.right = "10px";
                badge.style.backgroundColor = "#4a5568";
                badge.style.color = "white";
                badge.style.padding = "5px 10px";
                badge.style.borderRadius = "4px";
                badge.style.fontSize = "12px";
                badge.style.fontWeight = "bold";
                card.style.position = "relative";
                card.insertBefore(badge, img);
            }

            // PRODUCT NAME
            const title = document.createElement("h3");
            title.textContent = item.product;
            card.appendChild(title);

            // STORE
            const store = document.createElement("p");
            store.textContent = item.store;
            card.appendChild(store);

            // ORIGINAL PRICE (struck through if on sale)
            if (item.is_on_sale && item.original_price) {
                const old = document.createElement("p");
                old.textContent = "₹" + item.original_price;
                old.style.textDecoration = "line-through";
                old.style.color = "#999";
                old.style.fontSize = "14px";
                card.appendChild(old);
            }

            // PRICE
            const price = document.createElement("p");
            price.textContent = "₹" + item.price;

            if (parseFloat(item.price) === minPrice) {
                price.style.color = "green";
                price.textContent += " 🔥 Best Price";
            }

            card.appendChild(price);

            // BUTTON
            const btn = document.createElement("a");
            btn.href = item.store_url;
            btn.target = "_blank";
            btn.innerHTML = "<button>View Product</button>";
            card.appendChild(btn);

            container.appendChild(card);
        });
    }
}

// Search functionality
async function searchProduct() {
    let product = document.getElementById("productInput").value.trim();
    if (!product) { alert("Please enter a product name"); return; }

    try {
        const response = await fetch(`/price/${product}`);
        const data = await response.json();
        displayProducts(data);
    } catch (err) {
        console.error(err);
        alert("Failed to fetch prices");
    }
}