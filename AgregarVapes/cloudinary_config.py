import os
from pathlib import Path
from PIL import Image
import traceback

# Carpeta local para guardar imágenes
UPLOAD_FOLDER = Path(__file__).parent.parent / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def upload_image_to_cloud(local_path: str):
    """Copia imagen a static/uploads y devuelve ruta relativa."""
    try:
        if not os.path.exists(local_path):
            print(f"Archivo no existe: {local_path}")
            return None
        
        img = Image.open(local_path)
        filename = Path(local_path).name
        dest_path = UPLOAD_FOLDER / filename
        
        print(f"Guardando imagen en: {dest_path}")
        img.save(dest_path, quality=85, optimize=True)
        
        url = f"/static/uploads/{filename}"
        print(f"Imagen guardada. URL: {url}")
        return url
    except Exception as e:
        print("Error guardando imagen:", e)
        traceback.print_exc()
        return None

def upload_thumbnail(local_path: str):
    """Crea miniatura y la guarda localmente (convierte RGBA a RGB si es necesario)."""
    try:
        if not os.path.exists(local_path):
            print(f"Archivo no existe: {local_path}")
            return None
        
        img = Image.open(local_path)
        img.thumbnail((400, 400))
        
        # Convertir RGBA a RGB si es PNG o tiene transparencia
        if img.mode in ("RGBA", "LA", "P"):
            # Crear fondo blanco
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background
        
        filename = Path(local_path).stem + "_thumb.jpg"
        dest_path = UPLOAD_FOLDER / filename
        
        print(f"Guardando miniatura en: {dest_path}")
        img.save(dest_path, "JPEG", quality=85, optimize=True)
        
        url = f"/static/uploads/{filename}"
        print(f"Miniatura guardada. URL: {url}")
        return url
    except Exception as e:
        print("Error guardando miniatura:", e)
        traceback.print_exc()
        return None