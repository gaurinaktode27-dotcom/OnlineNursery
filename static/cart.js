// Initialize cart from localStorage
let cart = {};
try {
    const storedCart = localStorage.getItem('cart');
    if (storedCart) {
        cart = JSON.parse(storedCart);
    }
} catch (error) {
    console.error('Error loading cart from localStorage:', error);
    cart = {};
}

// Initialize popover when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize popover
    const popover = new bootstrap.Popover(document.getElementById('popcart'), {
        trigger: 'manual',
        html: true,
        placement: 'bottom',
        container: 'body',
        content: function() {
            return generateCartContent();
        }
    });

    // Handle cart button click
    document.getElementById('popcart').addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        popover.toggle();
    });

    // Close popover when clicking outside
    document.addEventListener('click', function(e) {
        const popcart = document.getElementById('popcart');
        const popoverElement = document.querySelector('.popover');
        
        if (!popcart.contains(e.target) && (!popoverElement || !popoverElement.contains(e.target))) {
            popover.hide();
        }
    });

    // Initial cart count update
    updateCartCount();
});

// Generate cart content
function generateCartContent() {
    let content = '<div class="cart-popover">';
    content += '<h5 style="color: #0c9c73; font-weight: bold; margin-bottom: 15px;">My Shopping Cart</h5>';
    content += '<div class="cart-items">';
    
    let i = 1;
    let totalAmount = 0;
    
    for (let item in cart) {
        if (cart[item][0] > 0) {
            const itemTotal = cart[item][0] * cart[item][2];
            totalAmount += itemTotal;
            
            content += `<div class="cart-item">
                <span class="item-number">${i}.</span>
                <span class="item-name">${cart[item][1]}</span>
                <span class="item-qty">Qty: ${cart[item][0]}</span>
                <span class="item-price">₹${itemTotal}</span>
            </div>`;
            i++;
        }
    }
    
    content += '</div>';
    
    if (i > 1) {
        content += `<div class="cart-total">
            <span>Total Amount:</span>
            <span class="total-amount">₹${totalAmount}</span>
        </div>`;
        
        content += `<div class="cart-buttons">
            <button class="btn btn-success checkout-btn" onclick="proceedToCheckout(${JSON.stringify(cart)}, ${totalAmount})">
                <i class="bi bi-bag-check"></i> Checkout
            </button>
            <button class="btn btn-danger clear-cart-btn" onclick="clearCart()">
                <i class="bi bi-trash"></i> Clear Cart
            </button>
        </div>`;
    } else {
        content += '<div class="empty-cart">Your cart is empty</div>';
    }
    
    content += '</div>';
    return content;
}

// Update cart count
function updateCartCount() {
    let sum = 0;
    for (let item in cart) {
        sum += cart[item][0];
    }
    document.getElementById('cart').textContent = sum;
}

// Handle cart button clicks
document.addEventListener('click', function(e) {
    if (e.target && e.target.classList.contains('cart')) {
        handleCartClick(e.target);
    } else if (e.target && e.target.classList.contains('minus')) {
        handleMinusClick(e.target);
    } else if (e.target && e.target.classList.contains('plus')) {
        handlePlusClick(e.target);
    }
});

// Handle cart button click
function handleCartClick(button) {
    const idstr = button.id.toString();
    const pid = parseInt(idstr.replace('pr', '').trim());
    const totalqty = parseInt(document.getElementById('qty' + pid).innerText);
    const price = parseFloat(document.getElementById('price' + pid).innerText.replace('Rs. ', '').trim());
    
    if (cart[idstr] !== undefined) {
        if (cart[idstr][0] < totalqty) {
            cart[idstr][0] += 1;
            cart[idstr][3] -= 1;
        } else {
            alert("Cannot add more than available quantity");
            return;
        }
    } else {
        cart[idstr] = [1, document.getElementById('name' + idstr).innerHTML, price, totalqty - 1, pid];
    }
    
    updateCart(cart);
}

// Handle minus button click
function handleMinusClick(button) {
    const id = button.id.replace('minus', '');
    if (cart[id][0] > 1) {
        cart[id][0]--;
        cart[id][3]++;
    } else {
        delete cart[id];
        document.getElementById('div' + id).innerHTML = `
            <button class='btn cart' id='${id}' 
                style="padding: 10px 16px; font-size: 16px; border-radius: 12px; background: linear-gradient(135deg, #0c9c73, #1abc9c); color: white; border: none; transition: all 0.3s ease; box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.2);"
                onmouseover="this.style.transform='scale(1.1)';" 
                onmouseout="this.style.transform='scale(1)';">
                Add to Cart
            </button>`;
    }
    updateCart(cart);
}

// Handle plus button click
function handlePlusClick(button) {
    const id = button.id.replace('plus', '');
    if (cart[id][0] < cart[id][3] + cart[id][0]) {
        cart[id][0]++;
        cart[id][3]--;
    } else {
        alert("Cannot add more than available quantity");
        return;
    }
    updateCart(cart);
}

// Update cart display
function updateCart(cart) {
    for (let item in cart) {
        if (cart[item][0] > 0) {
            document.getElementById('div' + item).innerHTML = `
                <button id='minus${item}' class='btn minus' 
                    style="padding: 8px 12px; font-size: 16px; border-radius: 12px; background: linear-gradient(135deg, #0c9c73, #1abc9c); color: white; border: none; transition: all 0.3s ease; box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.2);"
                    onmouseover="this.style.transform='scale(1.1)';" 
                    onmouseout="this.style.transform='scale(1)';">
                    -
                </button>
                <span id='val${item}' style="font-size: 16px; font-weight: bold; margin: 0 10px; color: #333;">${cart[item][0]}</span>
                <button id='plus${item}' class='btn plus' 
                    style="padding: 8px 12px; font-size: 16px; border-radius: 12px; background: linear-gradient(135deg, #0c9c73, #1abc9c); color: white; border: none; transition: all 0.3s ease; box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.2);"
                    onmouseover="this.style.transform='scale(1.1)';" 
                    onmouseout="this.style.transform='scale(1)';">
                    +
                </button>`;
        }
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    showCart();
}

// Show cart popup
function showCart() {
    let popStr = "<div class='cart-popover'>";
    popStr += "<h5 style='color: #0c9c73; font-weight: bold; margin-bottom: 15px;'>My Shopping Cart</h5>";
    popStr += "<div class='cart-items'>";
    let i = 1;
    let totalAmount = 0;
    let itemsJson = {};
    
    for (let item in cart) {
        if (cart[item][0] > 0) {
            popStr += `<div class='cart-item'>
                <span class='item-number'>${i}.</span>
                <span class='item-name'>${cart[item][1]}</span>
                <span class='item-qty'>Qty: ${cart[item][0]}</span>
                <span class='item-price'>₹${cart[item][2] * cart[item][0]}</span>
            </div>`;
            totalAmount += cart[item][0] * cart[item][2];
            itemsJson[item] = cart[item];
            i++;
        }
    }
    
    popStr += "</div>";
    
    if (i > 1) {
        popStr += `<div class='cart-total'>
            <span>Total Amount:</span>
            <span class='total-amount'>₹${totalAmount}</span>
        </div>`;
        
        popStr += `<div class='cart-buttons'>
            <button class='btn btn-success checkout-btn' onclick='proceedToCheckout(${JSON.stringify(itemsJson)}, ${totalAmount})'>
                <i class='bi bi-bag-check'></i> Checkout
            </button>
            <button class='btn btn-danger clear-cart-btn' onclick='clearCart()'>
                <i class='bi bi-trash'></i> Clear Cart
            </button>
        </div>`;
    } else {
        popStr += "<div class='empty-cart'>Your cart is empty</div>";
    }
    
    popStr += "</div>";
    
    // Create or update cart popup
    let cartPopup = document.getElementById('cart-popup');
    if (!cartPopup) {
        cartPopup = document.createElement('div');
        cartPopup.id = 'cart-popup';
        cartPopup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
            z-index: 1000;
            max-width: 90%;
            width: 400px;
            max-height: 80vh;
            overflow-y: auto;
        `;
        document.body.appendChild(cartPopup);
    }
    
    cartPopup.innerHTML = popStr;
    cartPopup.style.display = 'block';
    
    // Add overlay
    let overlay = document.getElementById('cart-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'cart-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 999;
        `;
        overlay.onclick = function() {
            cartPopup.style.display = 'none';
            overlay.style.display = 'none';
        };
        document.body.appendChild(overlay);
    }
    overlay.style.display = 'block';
}

// Clear cart
function clearCart() {
    cart = {};
    localStorage.removeItem('cart');
    updateCartCount();
    showCart();
}

// Proceed to checkout
function proceedToCheckout(itemsJson, totalAmount) {
    if (Object.keys(itemsJson).length === 0) {
        alert('Your cart is empty!');
        return;
    }
    
    // Store cart data in localStorage
    localStorage.setItem('checkoutItems', JSON.stringify(itemsJson));
    localStorage.setItem('checkoutAmount', totalAmount);
    
    // Create form and submit
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/checkout/';
    
    // Add CSRF token
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
    form.appendChild(csrfInput);
    
    // Add items JSON
    const itemsInput = document.createElement('input');
    itemsInput.type = 'hidden';
    itemsInput.name = 'itemsJson';
    itemsInput.value = JSON.stringify(itemsJson);
    form.appendChild(itemsInput);
    
    // Add amount
    const amountInput = document.createElement('input');
    amountInput.type = 'hidden';
    amountInput.name = 'checkoutAmount';
    amountInput.value = totalAmount;
    form.appendChild(amountInput);
    
    // Add updated quantities and pids
    const updatedQty = [];
    const pids = [];
    for (let item in itemsJson) {
        const pid = itemsJson[item][4]; // pid is at index 4
        const qty = itemsJson[item][0];
        const totalQty = itemsJson[item][3] + qty;
        updatedQty.push(totalQty);
        pids.push(pid);
    }
    
    const qtyInput = document.createElement('input');
    qtyInput.type = 'hidden';
    qtyInput.name = 'updatedqty';
    qtyInput.value = updatedQty.join(',');
    form.appendChild(qtyInput);
    
    const pidInput = document.createElement('input');
    pidInput.type = 'hidden';
    pidInput.name = 'pid';
    pidInput.value = pids.join(',');
    form.appendChild(pidInput);
    
    // Add form to document and submit
    document.body.appendChild(form);
    form.submit();
}

// Add styles for the cart popover
const style = document.createElement('style');
style.textContent = `
    .cart-popover {
        padding: 10px;
        min-width: 300px;
    }
    .cart-items {
        max-height: 300px;
        overflow-y: auto;
        margin-bottom: 15px;
    }
    .cart-item {
        display: flex;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #eee;
    }
    .item-number {
        width: 25px;
        color: #666;
    }
    .item-name {
        flex: 1;
        margin: 0 10px;
    }
    .item-qty {
        color: #666;
        margin-right: 10px;
    }
    .item-price {
        font-weight: bold;
        color: #0c9c73;
    }
    .cart-total {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-top: 2px solid #eee;
        font-weight: bold;
    }
    .total-amount {
        color: #0c9c73;
    }
    .cart-buttons {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }
    .checkout-btn, .clear-cart-btn {
        flex: 1;
        padding: 8px 15px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .checkout-btn:hover {
        background-color: #0a7d5d;
        transform: translateY(-2px);
    }
    .clear-cart-btn:hover {
        background-color: #dc3545;
        transform: translateY(-2px);
    }
    .empty-cart {
        text-align: center;
        color: #666;
        padding: 20px 0;
    }
`;
document.head.appendChild(style); 