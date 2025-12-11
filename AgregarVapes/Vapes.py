import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from .db_conn import init_db, insertar_producto, listar_productos
import os
import uuid
import shutil
from tkinter import filedialog
from PIL import Image, ImageTk  # pip install Pillow
from .cloudinary_config import upload_image_to_cloud, upload_thumbnail

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agregar Vapes - Productos")
        self.geometry("900x520")
        self.create_widgets()
        init_db()
        self.refresh_list()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10); frm.pack(fill="both", expand=True)
        left = ttk.Frame(frm); left.pack(side="left", fill="y", padx=(0,10))

        ttk.Label(left, text="Código (opcional)").grid(row=0, column=0, sticky="w")
        self.codigo = ttk.Entry(left, width=30); self.codigo.grid(row=1, column=0, pady=2)

        ttk.Label(left, text="Marca *").grid(row=2, column=0, sticky="w")
        self.marca = ttk.Entry(left, width=30); self.marca.grid(row=3, column=0, pady=2)

        ttk.Label(left, text="Sabor").grid(row=4, column=0, sticky="w")
        self.sabor = ttk.Entry(left, width=30); self.sabor.grid(row=5, column=0, pady=2)

        ttk.Label(left, text="Tipo").grid(row=6, column=0, sticky="w")
        self.tipo_var = tk.StringVar(value="Desechable")
        tipos = ["Desechable", "Recargable", "Pod", "Mod", "Otro"]
        ttk.OptionMenu(left, self.tipo_var, self.tipo_var.get(), *tipos).grid(row=7, column=0, pady=2, sticky="we")

        ttk.Label(left, text="Stock").grid(row=8, column=0, sticky="w")
        self.stock = ttk.Entry(left, width=30); self.stock.insert(0, "0"); self.stock.grid(row=9, column=0, pady=2)

        ttk.Label(left, text="Precio").grid(row=10, column=0, sticky="w")
        self.precio = ttk.Entry(left, width=30); self.precio.insert(0, "0.00"); self.precio.grid(row=11, column=0, pady=2)

        ttk.Label(left, text="Descripción").grid(row=12, column=0, sticky="w")
        self.descripcion = scrolledtext.ScrolledText(left, width=30, height=6); self.descripcion.grid(row=13, column=0, pady=2)

        ttk.Label(left, text="Imagen (opcional)").grid(row=15, column=0, sticky="w")
        img_frame = ttk.Frame(left); img_frame.grid(row=16, column=0, pady=2)
        ttk.Button(img_frame, text="Seleccionar imagen...", command=self.select_image).pack(side="left")
        self.img_label = ttk.Label(img_frame, text="No hay imagen")
        self.img_label.pack(side="left", padx=6)

        btn_frame = ttk.Frame(left); btn_frame.grid(row=14, column=0, pady=8, sticky="we")
        ttk.Button(btn_frame, text="Guardar", command=self.on_guardar).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar).pack(side="left", expand=True, fill="x", padx=2)

        right = ttk.Frame(frm); right.pack(side="right", fill="both", expand=True)
        ttk.Label(right, text="Productos (recientes)").pack(anchor="w")
        self.tree = ttk.Treeview(right, columns=("id","codigo","marca","sabor","tipo","stock","precio"), show="headings", selectmode="browse")
        for col, w in [("id",50), ("codigo",120), ("marca",150), ("sabor",140), ("tipo",100), ("stock",70), ("precio",90)]:
            self.tree.heading(col, text=col.capitalize()); self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True)
        ttk.Button(right, text="Refrescar", command=self.refresh_list).pack(pady=6)

    def limpiar(self):
        self.codigo.delete(0, "end"); self.marca.delete(0, "end"); self.sabor.delete(0, "end")
        self.tipo_var.set("Desechable"); self.stock.delete(0, "end"); self.stock.insert(0, "0")
        self.precio.delete(0, "end"); self.precio.insert(0, "0.00"); self.descripcion.delete("1.0", "end")
        self.img_label.config(text="No hay imagen")  # Reset image label

    def select_image(self):
        # Validación de tipos y tamaño antes de copiar
        path = filedialog.askopenfilename(filetypes=[("Imagen","*.png;*.jpg;*.jpeg;*.webp;*.gif")])
        if not path:
            return

        ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
        MAX_BYTES = 5 * 1024 * 1024       # 5 MB
        MAX_DIM = 2000                    # px (anchura/alto máximo)

        ext = os.path.splitext(path)[1].lower()
        if ext not in ALLOWED_EXT:
            messagebox.showerror("Imagen no válida", f"Tipo de archivo no permitido: {ext}")
            return

        size = os.path.getsize(path)
        if size > MAX_BYTES:
            messagebox.showerror("Imagen demasiado grande", "La imagen supera el límite de 5 MB.")
            return

        # crear carpeta media/images si no existe
        media_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "media", "images"))
        os.makedirs(media_dir, exist_ok=True)
        new_name = f"{uuid.uuid4().hex}{ext}"
        dest = os.path.join(media_dir, new_name)

        # Intentar abrir y procesar con Pillow (verifica que sea una imagen real)
        try:
            img = Image.open(path)
            img.verify()  # verifica integridad básica
            img = Image.open(path)  # reabrir para operaciones
        except Exception:
            messagebox.showerror("Imagen inválida", "No se pudo abrir la imagen. Formato o archivo corrupto.")
            return

        # Redimensionar si es muy grande y guardar copia
        try:
            # re-open ensures image is usable for operations
            img = Image.open(path)
            w, h = img.size
            if max(w, h) > MAX_DIM:
                ratio = MAX_DIM / float(max(w, h))
                new_size = (int(w * ratio), int(h * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            # Guardar copia optimizada
            save_kwargs = {}
            if ext in (".jpg", ".jpeg"):
                save_kwargs = {"quality": 85}
                if img.mode in ("RGBA", "LA"):
                    img = img.convert("RGB")
            img.save(dest, optimize=True, **save_kwargs)
        except Exception:
            messagebox.showerror("Error", "No se pudo procesar o guardar la imagen.")
            return

        # crear miniatura
        try:
            thumb_path = os.path.join(media_dir, f"thumb_{new_name}")
            thumb = Image.open(dest)
            thumb.thumbnail((200, 200), Image.LANCZOS)
            if thumb.mode in ("RGBA", "LA") and ext in (".jpg", ".jpeg"):
                thumb = thumb.convert("RGB")
            thumb.save(thumb_path, optimize=True, quality=85)
        except Exception:
            thumb_path = None

        # guardar referencias temporales en la instancia
        self._selected_image = dest
        self._selected_thumb = thumb_path
        self._selected_mime = Image.MIME.get(img.format) if hasattr(img, "format") else None
        self._selected_size = os.path.getsize(dest)

        # actualizar etiqueta
        self.img_label.config(text=os.path.basename(dest))

    def on_guardar(self):
        marca_val = self.marca.get().strip()
        if not marca_val:
            messagebox.showwarning("Validación", "La marca es obligatoria.")
            return
        
        image_url = None
        thumb_url = None
        
        # Si hay imagen seleccionada, subirla a Cloudinary
        if hasattr(self, "_selected_image"):
            print(f"DEBUG: Imagen seleccionada: {self._selected_image}")
            image_url = upload_image_to_cloud(self._selected_image)
            print(f"DEBUG: image_url retornada: {image_url}")
            thumb_url = upload_thumbnail(self._selected_image)
            print(f"DEBUG: thumb_url retornada: {thumb_url}")
            
            if not image_url:
                messagebox.showerror("Error", "No se pudo subir la imagen a la nube")
                return
        
        data = {
            "codigo": self.codigo.get().strip() or None,
            "marca": marca_val,
            "sabor": self.sabor.get().strip(),
            "tipo": self.tipo_var.get(),
            "stock": self.stock.get().strip(),
            "precio": self.precio.get().strip(),
            "descripcion": self.descripcion.get("1.0", "end").strip(),
            "image_url": image_url,  # URL pública de Cloudinary
            "image_thumb_url": thumb_url,  # URL pública de miniatura
            "image_mime": "image/jpeg",
            "image_size": None,
        }
        
        ok, msg = insertar_producto(data)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.limpiar()
            self.refresh_list()
        else:
            messagebox.showerror("Error", msg)

    def refresh_list(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        rows = listar_productos(500)
        for r in rows:
            precio = float(r.get("precio") or 0.0)
            self.tree.insert("", "end", values=(r.get("id"), r.get("codigo"), r.get("marca"), r.get("sabor"), r.get("tipo"), r.get("stock"), f"{precio:.2f}"))

if __name__ == "__main__":
    app = App(); app.mainloop()