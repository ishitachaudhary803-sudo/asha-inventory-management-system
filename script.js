const rows = document.getElementById("productRows");
const searchInput = document.getElementById("searchInput");
const dialog = document.getElementById("productDialog");
const form = document.getElementById("productForm");
const toast = document.getElementById("toast");
let allProducts = [];
let toastTimer;

const money = value => new Intl.NumberFormat("en-IN", {
  style: "currency", currency: "INR", maximumFractionDigits: 2
}).format(value);

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

async function loadProducts() {
  try {
    allProducts = await api("/api/products");
    renderProducts();
    updateStats();
  } catch (error) {
    rows.innerHTML = `<tr><td colspan="7" class="empty-state">Could not load products. Refresh the page and try again.</td></tr>`;
    showToast(error.message);
  }
}

function updateStats() {
  document.getElementById("totalProducts").textContent = allProducts.length;
  document.getElementById("totalUnits").textContent =
    allProducts.reduce((sum, item) => sum + Number(item.quantity), 0).toLocaleString("en-IN");
  document.getElementById("lowStock").textContent =
    allProducts.filter(item => Number(item.quantity) <= 5).length;
  const value = allProducts.reduce((sum, item) => sum + Number(item.price) * Number(item.quantity), 0);
  document.getElementById("inventoryValue").textContent = money(value);
}

function safeText(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));
}

function renderProducts() {
  const query = searchInput.value.trim().toLowerCase();
  const products = allProducts.filter(item =>
    [item.name, item.sku, item.category].some(value => String(value).toLowerCase().includes(query))
  );
  document.getElementById("resultCount").textContent = `${products.length} product${products.length === 1 ? "" : "s"}`;
  document.getElementById("footerCount").textContent = `Showing ${products.length} of ${allProducts.length} products`;

  if (!products.length) {
    rows.innerHTML = `<tr><td colspan="7" class="empty-state">${query ? "No matching products found." : "No products yet. Add your first product above."}</td></tr>`;
    return;
  }

  rows.innerHTML = products.map(item => {
    const quantity = Number(item.quantity);
    const status = quantity === 0
      ? '<span class="pill pill-out">Out of stock</span>'
      : quantity <= 5
        ? '<span class="pill pill-low">Low stock</span>'
        : '<span class="pill pill-ok">In stock</span>';
    const initial = safeText(item.name.trim().slice(0, 1).toUpperCase() || "P");
    return `<tr>
      <td><div class="product-cell"><div class="product-avatar">${initial}</div><div><div class="product-name">${safeText(item.name)}</div><div class="product-description">${safeText(item.description || "No description added")}</div></div></div></td>
      <td class="sku">${safeText(item.sku)}</td>
      <td>${safeText(item.category)}</td>
      <td class="price">${money(Number(item.price))}</td>
      <td><span class="stock-count ${quantity <= 5 ? "stock-low" : "stock-good"}">${quantity}</span></td>
      <td>${status}</td>
      <td><div class="actions"><button class="action-btn" data-edit="${item.id}">Edit</button><button class="action-btn delete" data-delete="${item.id}">Delete</button></div></td>
    </tr>`;
  }).join("");
}

function openAddDialog() {
  form.reset();
  document.getElementById("productId").value = "";
  document.getElementById("dialogTitle").textContent = "Add product";
  document.getElementById("saveButton").textContent = "Save product";
  document.getElementById("formError").textContent = "";
  dialog.showModal();
}

function openEditDialog(item) {
  form.reset();
  document.getElementById("productId").value = item.id;
  document.getElementById("name").value = item.name;
  document.getElementById("sku").value = item.sku;
  document.getElementById("category").value = item.category;
  document.getElementById("price").value = item.price;
  document.getElementById("quantity").value = item.quantity;
  document.getElementById("description").value = item.description;
  document.getElementById("dialogTitle").textContent = "Edit product";
  document.getElementById("saveButton").textContent = "Update product";
  document.getElementById("formError").textContent = "";
  dialog.showModal();
}

document.getElementById("addButton").addEventListener("click", openAddDialog);
document.getElementById("closeDialog").addEventListener("click", () => dialog.close());
document.getElementById("cancelButton").addEventListener("click", () => dialog.close());
searchInput.addEventListener("input", renderProducts);

rows.addEventListener("click", async event => {
  const editButton = event.target.closest("[data-edit]");
  const deleteButton = event.target.closest("[data-delete]");
  if (editButton) {
    const item = allProducts.find(product => product.id === Number(editButton.dataset.edit));
    if (item) openEditDialog(item);
  }
  if (deleteButton) {
    const item = allProducts.find(product => product.id === Number(deleteButton.dataset.delete));
    if (!item) return;
    if (!confirm(`Delete "${item.name}" from the catalogue?`)) return;
    try {
      await api(`/api/products/${item.id}`, { method: "DELETE" });
      showToast("Product deleted.");
      await loadProducts();
    } catch (error) {
      showToast(error.message);
    }
  }
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  const id = document.getElementById("productId").value;
  const payload = {
    name: document.getElementById("name").value.trim(),
    sku: document.getElementById("sku").value.trim(),
    category: document.getElementById("category").value.trim() || "General",
    price: document.getElementById("price").value,
    quantity: document.getElementById("quantity").value,
    description: document.getElementById("description").value.trim()
  };
  const errorBox = document.getElementById("formError");
  errorBox.textContent = "";
  try {
    await api(id ? `/api/products/${id}` : "/api/products", {
      method: id ? "PUT" : "POST",
      body: JSON.stringify(payload)
    });
    dialog.close();
    showToast(id ? "Product updated successfully." : "Product added successfully.");
    await loadProducts();
  } catch (error) {
    errorBox.textContent = error.message;
  }
});

loadProducts();
