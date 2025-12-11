document.addEventListener('DOMContentLoaded', () => {
    attachCarritoButtons();
    actualizarBadge();
});

function attachCarritoButtons() {
    document.querySelectorAll('.btn-carrito').forEach(btn => {
        btn.removeEventListener('click', btn._cartHandler);
        const handler = function (e) {
            const id = this.dataset.id;
            const nombre = this.dataset.nombre;
            const sabor = this.dataset.sabor || '';
            const precio = parseFloat(this.dataset.precio) || 0;
            const imagen = this.dataset.imagen || '/static/placeholder.png';
            agregarCarrito(id, nombre, sabor, precio, imagen);
        };
        btn._cartHandler = handler;
        btn.addEventListener('click', handler);
    });
}

function agregarCarrito(id, nombre, sabor, precio, imagen) {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const existente = carrito.find(item => item.id == id);
    if (existente) {
        existente.cantidad = (existente.cantidad || 1) + 1;
    } else {
        carrito.push({ 
            id: id, 
            marca: nombre, 
            sabor: sabor, 
            precio: precio, 
            imagen_url: imagen,
            cantidad: 1 
        });
    }
    localStorage.setItem('carrito', JSON.stringify(carrito));
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