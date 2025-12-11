document.addEventListener('DOMContentLoaded', function() {
    cargarCarrito();

    const btnCheckout = document.querySelector('.btn-checkout');
    if (btnCheckout) {
        btnCheckout.addEventListener('click', function() {
            procederCheckout();
        });
    }

    actualizarBadge();
});

function cargarCarrito() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const itemsContainer = document.getElementById('carrito-items');
    const vacioDIV = document.getElementById('carrito-vacio');
    const resumenDIV = document.getElementById('carrito-resumen');

    itemsContainer.innerHTML = '';

    if (carrito.length === 0) {
        vacioDIV.style.display = 'block';
        resumenDIV.style.display = 'none';
        return;
    }

    vacioDIV.style.display = 'none';
    resumenDIV.style.display = 'block';

    let subtotal = 0;

    carrito.forEach((item, index) => {
        const total = item.precio * item.cantidad;
        subtotal += total;

        // Usar imagen_url si existe, sino placeholder
        const imgSrc = item.imagen_url || '/static/placeholder.png';

        const itemHTML = `
            <div class="carrito-item">
                <div class="carrito-item-img">
                    <img src="${imgSrc}" alt="${item.marca}" onerror="this.src='/static/placeholder.png'">
                </div>
                <div class="carrito-item-info">
                    <h4>${item.marca}</h4>
                    <p>${item.sabor || 'Sin sabor'}</p>
                </div>
                <div class="carrito-item-cantidad">
                    <button onclick="cambiarCantidad(${index}, -1)">−</button>
                    <input type="number" value="${item.cantidad}" min="1" onchange="actualizarCantidad(${index}, this.value)">
                    <button onclick="cambiarCantidad(${index}, 1)">+</button>
                </div>
                <div class="carrito-item-precio">$${total.toFixed(2)}</div>
                <button class="carrito-item-eliminar" onclick="eliminarItem(${index})">✕</button>
            </div>
        `;
        itemsContainer.innerHTML += itemHTML;
    });

    document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('total').textContent = `$${subtotal.toFixed(2)}`;
}

function cambiarCantidad(index, cambio) {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    carrito[index].cantidad += cambio;
    if (carrito[index].cantidad < 1) carrito[index].cantidad = 1;
    localStorage.setItem('carrito', JSON.stringify(carrito));
    cargarCarrito();
    actualizarBadge();
}

function actualizarCantidad(index, nuevaCantidad) {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    carrito[index].cantidad = parseInt(nuevaCantidad) || 1;
    localStorage.setItem('carrito', JSON.stringify(carrito));
    cargarCarrito();
    actualizarBadge();
}

function eliminarItem(index) {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    carrito.splice(index, 1);
    localStorage.setItem('carrito', JSON.stringify(carrito));
    cargarCarrito();
    actualizarBadge();
}

function actualizarBadge() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const total = carrito.reduce((sum, item) => sum + item.cantidad, 0);
    const badges = document.querySelectorAll('#cart-badge');
    
    badges.forEach(badge => {
        if (total > 0) {
            badge.style.display = 'inline-flex';
            badge.textContent = total;
        } else {
            badge.style.display = 'none';
        }
    });
}

async function procederCheckout() {
    // Detectar si está logueado (si existe "Cerrar sesión" en el HTML)
    const loggedIn = document.body.innerHTML.includes('Cerrar sesión');
    
    if (!loggedIn) {
        window.location.href = '/auth';
        return;
    }

    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    if (!carrito.length) {
        alert('El carrito está vacío.');
        return;
    }

    try {
        const resp = await fetch('/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cart: carrito })
        });

        const data = await resp.json();
        if (!resp.ok) {
            const msg = data.error || data.detail || 'Error al procesar el pedido';
            alert('Error: ' + msg);
            return;
        }

        localStorage.removeItem('carrito');
        alert('✅ Pedido registrado. ID: ' + data.order_id);
        actualizarBadge();
        window.location.href = '/diseño';
    } catch (err) {
        console.error(err);
        alert('Error de red al enviar el pedido.');
    }
}