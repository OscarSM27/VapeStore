
1. Crear entorno virtual

```bash
cd "C:\Users\Usuario\OneDrive\Escritorio\vapes"
python -m venv venv
```

### 2. Activar entorno virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate
```

### 3. Instalar dependencias

```bash
pip install flask pymysql pillow
```

### 4. Crear carpeta para subidas de imágenes

```powershell
mkdir static\uploads
```

---

## 🏃 Ejecución

### Opción 1: Solo la tienda web

```powershell
python web_app.py
```

Luego abre en el navegador:
```
http://127.0.0.1:5000/diseño
```

### Opción 2: Solo agregar productos (GUI Tkinter)

```powershell
python -m AgregarVapes.Vapes
```

### Opción 3: Ambas simultáneamente (recomendado)

**Terminal 1 - Servidor web:**
```powershell
python web_app.py
```

**Terminal 2 - Interfaz gráfica (en otra terminal):**
```powershell
python -m AgregarVapes.Vapes
```

---

## 📁 Estructura del Proyecto

```
vapes/
├── AgregarVapes/
│   ├── __init__.py
│   ├── Vapes.py              # Interfaz Tkinter para agregar productos
│   ├── db_conn.py            # Conexión a BD desde la GUI
│   └── cloudinary_config.py  # Funciones para guardar imágenes
│
├── db/
│   ├── __init__.py
│   └── main.py               # Conexión a MySQL y funciones de usuario
│
├── static/
│   ├── style.css             # Estilos CSS de la web
│   ├── script.js             # JavaScript para carrito
│   ├── carrito.js            # Gestión del carrito
│   ├── placeholder.png       # Imagen por defecto
│   └── uploads/              # Carpeta de imágenes subidas
│
├── templates/
│   ├── Diseño.html           # Página principal con productos
│   ├── auth.html             # Login/Registro
│   ├── carrito.html          # Página del carrito
│   └── productos.html        # Listado de productos (opcional)
│
├── web_app.py                # Servidor Flask
├── requirements.txt          # Dependencias del proyecto
├── # Vapes Store - Tienda en línea

## 🚀 Despliegue en Render (GRATIS)

### Pasos para poner tu sitio en línea:

1. **Crea una cuenta en Render:**
   - Ve a https://render.com
   - Regístrate con tu cuenta de GitHub, GitLab o email

2. **Sube tu código a GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <tu-repositorio-github>
   git push -u origin main
   ```

3. **En Render Dashboard:**
   - Click en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub
   - Configura:
     * **Name:** vapes-store (o el nombre que prefieras)
     * **Environment:** Python 3
     * **Build Command:** `pip install -r requirements.txt`
     * **Start Command:** `gunicorn web_app:app`
     * **Plan:** Free

4. **Variables de Entorno (Environment Variables):**
   En la sección "Environment", agrega:
   - `SECRET_KEY` = (genera una clave secreta segura)
   - `PYTHON_VERSION` = 3.11.7

5. **Despliega:**
   - Click en "Create Web Service"
   - Render automáticamente desplegará tu aplicación
   - En unos minutos tendrás tu URL pública: `https://vapes-store.onrender.com`

---

## 🌐 Otras opciones de hosting gratuito:

### Railway (Alternativa recomendada)
1. Ve a https://railway.app
2. Conecta con GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Railway detecta automáticamente Flask
5. URL pública disponible en segundos

### PythonAnywhere (Más tradicional)
1. Cuenta gratuita en https://www.pythonanywhere.com
2. Sube archivos o clona desde GitHub
3. Configura WSGI file para Flask
4. Tu sitio estará en: `https://tusername.pythonanywhere.com`

---

## 📋 Requisitos

Tu aplicación ya está lista para producción con:
- ✅ Base de datos MySQL configurada (Aiven Cloud)
- ✅ Gunicorn como servidor WSGI
- ✅ Variables de entorno para seguridad
- ✅ Archivos de configuración (Procfile, requirements.txt)

---

## 🔧 Desarrollo local

```bash
pip install -r requirements.txt
python web_app.py
```

Visita: http://localhost:5000

---

## 📝 Notas importantes

- La base de datos ya está en la nube (Aiven), funcionará desde cualquier lugar
- Render toma ~2 minutos en desplegar
- El plan gratuito de Render puede dormir después de 15 min de inactividad
- La primera carga después de dormir toma ~30 segundos                 # Este archivo
└── venv/                     # Entorno virtual (no subir a Git)
```

### Las imágenes no se ven
1. Verifica que exista la carpeta `static/uploads/`
2. Comprueba que la imagen_url en BD empiece con `/static/uploads/`
3. Abre directamente: `http://127.0.0.1:5000/static/uploads/imagen.jpg`


## 📝 Notas

- El carrito se guarda en `localStorage` del navegador (no requiere servidor)
- Las imágenes se guardan en `static/uploads/` (carpeta local)
- Para producción, considera usar Cloudinary u otro servicio de almacenamiento en la nube
.