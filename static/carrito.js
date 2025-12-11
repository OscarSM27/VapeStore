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

    // Mostrar modal de envío
    const modal = document.getElementById('modalEnvio');
    modal.style.display = 'flex';
}

// Variables globales para almacenar datos del pedido
let datosEnvio = {};

// Cerrar modales y manejar formularios
document.addEventListener('DOMContentLoaded', function() {
    // Botón cancelar modal de envío
    const btnCancelar = document.getElementById('btnCancelarModal');
    if (btnCancelar) {
        btnCancelar.addEventListener('click', function() {
            document.getElementById('modalEnvio').style.display = 'none';
            document.getElementById('formEnvio').reset();
        });
    }

    // Botón cancelar modal de pago
    const btnCancelarPago = document.getElementById('btnCancelarPago');
    if (btnCancelarPago) {
        btnCancelarPago.addEventListener('click', function() {
            document.getElementById('modalPago').style.display = 'none';
        });
    }

    // Manejar envío del formulario de dirección
    const formEnvio = document.getElementById('formEnvio');
    if (formEnvio) {
        formEnvio.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const direccion = document.getElementById('direccion').value.trim();
            const referencias = document.getElementById('referencias').value.trim();
            const telefono = document.getElementById('telefono').value.trim();

            if (!direccion || !referencias || !telefono) {
                alert('Por favor completa todos los campos');
                return;
            }

            // Validar teléfono (10 dígitos)
            if (!/^\d{10}$/.test(telefono)) {
                alert('El teléfono debe tener 10 dígitos');
                return;
            }

            // Guardar datos de envío
            datosEnvio = {
                direccion: direccion,
                referencias: referencias,
                telefono: telefono
            };

            // Ocultar modal de envío y mostrar modal de pago
            document.getElementById('modalEnvio').style.display = 'none';
            document.getElementById('modalPago').style.display = 'flex';
        });
    }

    // Botón Efectivo
    const btnEfectivo = document.getElementById('btnEfectivo');
    if (btnEfectivo) {
        btnEfectivo.addEventListener('click', function() {
            procesarPedido('efectivo');
        });
    }

    // Botón Tarjeta
    const btnTarjeta = document.getElementById('btnTarjeta');
    if (btnTarjeta) {
        btnTarjeta.addEventListener('click', function() {
            procesarPedido('tarjeta');
        });
    }
});

// Función para procesar el pedido con el método de pago seleccionado
async function procesarPedido(metodoPago) {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];

    try {
        const resp = await fetch('/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                cart: carrito,
                direccion: datosEnvio.direccion,
                referencias: datosEnvio.referencias,
                telefono: datosEnvio.telefono,
                metodo_pago: metodoPago
            })
        });

        const data = await resp.json();
        if (!resp.ok) {
            const msg = data.error || data.detail || 'Error al procesar el pedido';
            alert('Error: ' + msg);
            return;
        }

        localStorage.removeItem('carrito');
        document.getElementById('modalPago').style.display = 'none';
        document.getElementById('formEnvio').reset();
        datosEnvio = {};
        actualizarBadge();
        
        // Mostrar modal de éxito
        const modalExito = document.getElementById('modalExito');
        modalExito.style.display = 'flex';
        
        // Cerrar modal y redirigir después de 3 segundos
        setTimeout(function() {
            modalExito.style.display = 'none';
            window.location.href = '/';
        }, 3000);
    } catch (err) {
        console.error(err);
        alert('Error de red al enviar el pedido.');
    }
}