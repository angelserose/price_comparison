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

            // PRODUCT NAME
            const title = document.createElement("h3");
            title.textContent = item.product;
            card.appendChild(title);

            // STORE
            const store = document.createElement("p");
            store.textContent = item.store;
            card.appendChild(store);

            // PRICE
            const price = document.createElement("p");
            price.textContent = "₹" + item.price;

            if (parseFloat(item.price) === minPrice) {
                price.style.color = "green";
                price.textContent += " 🔥 Best Price";
            }

            card.appendChild(price);

            // OLD PRICE + DISCOUNT
            if (item.old_price && item.old_price > item.price) {
                const old = document.createElement("p");
                old.textContent = "₹" + item.old_price;
                old.style.textDecoration = "line-through";
                card.appendChild(old);

                const discount = document.createElement("p");
                discount.textContent =
                    Math.round(((item.old_price - item.price) / item.old_price) * 100) + "% OFF";
                discount.style.color = "red";
                card.appendChild(discount);
            }

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