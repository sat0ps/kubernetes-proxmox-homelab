const api = "/api";

async function loadOrders() {
  const response = await fetch(`${api}/orders`);
  if (!response.ok) throw new Error("Unable to load orders");
  const orders = await response.json();
  document.querySelector("#orders").innerHTML = orders
    .map(o => `<tr><td>${o.id}</td><td>${o.customer}</td><td>${o.item}</td><td>${o.quantity}</td></tr>`)
    .join("");
}

document.querySelector("#order-form").addEventListener("submit", async event => {
  event.preventDefault();
  const status = document.querySelector("#status");
  const payload = {
    customer: document.querySelector("#customer").value,
    item: document.querySelector("#item").value,
    quantity: Number(document.querySelector("#quantity").value)
  };
  const response = await fetch(`${api}/orders`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  status.textContent = response.ok ? "Order created" : "Order creation failed";
  if (response.ok) {
    event.target.reset();
    document.querySelector("#quantity").value = 1;
    await loadOrders();
  }
});

loadOrders().catch(error => {
  document.querySelector("#status").textContent = error.message;
});
