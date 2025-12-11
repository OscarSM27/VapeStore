import os
from pathlib import Path

# Cargar variables de entorno del archivo .env ANTES de importar cualquier módulo
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

from flask import Flask, render_template, abort, url_for, request, session, redirect, jsonify
from db.main import get_connection, register_user, get_user_by_email
import hashlib
import traceback

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "tu_clave_secreta_super_segura_123")

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def fetch_products(limit=100, random=False):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if random:
                cur.execute(
                    "SELECT id, codigo, marca, sabor, tipo, stock, precio, descripcion, image_url, thumb_url, fecha_ingreso "
                    "FROM productos ORDER BY RAND() LIMIT %s", (limit,)
                )
            else:
                cur.execute(
                    "SELECT id, codigo, marca, sabor, tipo, stock, precio, descripcion, image_url, thumb_url, fecha_ingreso "
                    "FROM productos ORDER BY fecha_ingreso DESC LIMIT %s", (limit,)
                )
            return cur.fetchall()
    finally:
        conn.close()

def fetch_product(product_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, codigo, marca, sabor, tipo, stock, precio, descripcion, image_url, thumb_url, fecha_ingreso "
                "FROM productos WHERE id = %s LIMIT 1", (product_id,)
            )
            return cur.fetchone()
    finally:
        conn.close()

@app.route("/producto/<int:product_id>")
def producto(product_id):
    p = fetch_product(product_id)
    if not p:
        abort(404)
    return render_template("producto.html", product=p)

@app.route("/auth", methods=["GET", "POST"])
def auth():
    return render_template("auth.html")

@app.route("/auth/login", methods=["POST"])
def auth_login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    
    if not email or not password:
        return render_template("auth.html", error="Email y contraseña requeridos"), 400
    
    user = get_user_by_email(email)
    if user:
        # Compara el hash de la contraseña ingresada con la guardada
        if user.get("password") == _hash_password(password):
            session["user_id"] = user.get("id")
            session["user_name"] = user.get("name")
            return redirect(url_for("index"))
    
    # Si llegamos aquí, las credenciales son inválidas
    return render_template("auth.html", error="Email o contraseña incorrectos"), 401

@app.route("/auth/registro", methods=["POST"])
def auth_registro():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()
    
    if not name or not email or not password or not confirm_password:
        return render_template("auth.html", error="Todos los campos son requeridos"), 400
    
    if password != confirm_password:
        return render_template("auth.html", error="Las contraseñas no coinciden"), 400
    
    if len(password) < 6:
        return render_template("auth.html", error="La contraseña debe tener al menos 6 caracteres"), 400
    
    try:
        user = register_user(name, email, password)
        session["user_id"] = user.get("id")
        session["user_name"] = user.get("name")
        return redirect(url_for("index"))
    except Exception as e:
        error_msg = str(e)
        if "Duplicate entry" in error_msg or "email" in error_msg.lower():
            return render_template("auth.html", error="Este email ya está registrado"), 400
        return render_template("auth.html", error=f"Error en el registro: {error_msg}"), 400

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/")
def index():
    # Obtener 4 productos aleatorios para la página de inicio
    productos_destacados = fetch_products(4, random=True)
    return render_template("inicio.html", productos_destacados=productos_destacados)

@app.route("/carrito")
def carrito():
    # Mostrar la página del carrito aunque no se esté logueado
    return render_template(
        "carrito.html",
        logged_in=bool(session.get("user_id")),
        user_name=session.get("user_name")
    )

@app.route("/checkout", methods=["POST"])
def checkout():
    if not session.get("user_id"):
        return jsonify({"error": "login_required"}), 401

    data = request.get_json() or {}
    cart = data.get("cart") or []
    direccion = data.get("direccion", "").strip()
    referencias = data.get("referencias", "").strip()
    telefono = data.get("telefono", "").strip()
    metodo_pago = data.get("metodo_pago", "").strip()
    
    if not cart:
        return jsonify({"error": "carrito_vacio"}), 400
    
    if not direccion or not referencias or not telefono:
        return jsonify({"error": "datos_envio_incompletos"}), 400
    
    if not metodo_pago or metodo_pago not in ['efectivo', 'tarjeta']:
        return jsonify({"error": "metodo_pago_invalido"}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            items = []
            subtotal = 0.0
            for it in cart:
                try:
                    pid = int(it.get("id"))
                    qty = int(it.get("cantidad", it.get("cantidad", 1)))
                except Exception:
                    return jsonify({"error": "datos_producto_invalidos"}), 400

                if qty < 1:
                    return jsonify({"error": f"cantidad_invalida_producto_{pid}"}), 400

                cur.execute("SELECT precio, stock FROM productos WHERE id = %s LIMIT 1", (pid,))
                prod = cur.fetchone()
                if not prod:
                    return jsonify({"error": f"producto_no_encontrado_{pid}"}), 400

                price = float(prod.get("precio") or 0)
                stock = int(prod.get("stock") or 0)
                if stock < qty:
                    return jsonify({"error": f"stock_insuficiente_producto_{pid}"}), 400

                line_total = price * qty
                subtotal += line_total
                items.append({"product_id": pid, "qty": qty, "price": price})

            tax = round(subtotal * 0.10, 2)
            total = round(subtotal + tax, 2)

            cur.execute(
                "INSERT INTO orders (user_id, total, tax, direccion_envio, referencias, telefono, metodo_pago) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (session["user_id"], total, tax, direccion, referencias, telefono, metodo_pago)
            )
            order_id = cur.lastrowid

            for it in items:
                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                    (order_id, it["product_id"], it["qty"], it["price"])
                )
                cur.execute(
                    "UPDATE productos SET stock = stock - %s WHERE id = %s",
                    (it["qty"], it["product_id"])
                )

            conn.commit()
            return jsonify({"ok": True, "order_id": order_id}), 200

    except Exception as e:
        conn.rollback()
        traceback.print_exc()
        return jsonify({"error": "server_error", "detail": str(e)}), 500
    finally:
        conn.close()

# alias sin tilde (útil para evitar problemas con URLs/endpoint Unicode)
@app.route("/diseno")
def diseno_alias():
    return redirect(url_for("diseño"))

@app.route("/diseño")
def diseño():
    products = fetch_products(200)
    return render_template("Diseño.html", products=products)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)