"""
Script para agregar columnas de información de envío a la tabla orders
"""
import os
from pathlib import Path

# Cargar variables de entorno del archivo .env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

from db.main import get_connection

def actualizar_tabla_orders():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Verificar si las columnas ya existen
            cur.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'orders' 
                AND COLUMN_NAME IN ('direccion_envio', 'referencias', 'telefono', 'metodo_pago')
            """, (os.environ.get("DB_NAME", "Vapes"),))
            
            existing_columns = [row['COLUMN_NAME'] for row in cur.fetchall()]
            
            # Agregar columnas si no existen
            if 'direccion_envio' not in existing_columns:
                cur.execute("ALTER TABLE orders ADD COLUMN direccion_envio VARCHAR(500)")
                print("✅ Columna 'direccion_envio' agregada")
            else:
                print("ℹ️  Columna 'direccion_envio' ya existe")
            
            if 'referencias' not in existing_columns:
                cur.execute("ALTER TABLE orders ADD COLUMN referencias TEXT")
                print("✅ Columna 'referencias' agregada")
            else:
                print("ℹ️  Columna 'referencias' ya existe")
            
            if 'telefono' not in existing_columns:
                cur.execute("ALTER TABLE orders ADD COLUMN telefono VARCHAR(20)")
                print("✅ Columna 'telefono' agregada")
            else:
                print("ℹ️  Columna 'telefono' ya existe")
            
            if 'metodo_pago' not in existing_columns:
                cur.execute("ALTER TABLE orders ADD COLUMN metodo_pago VARCHAR(20)")
                print("✅ Columna 'metodo_pago' agregada")
            else:
                print("ℹ️  Columna 'metodo_pago' ya existe")
            
        conn.commit()
        print("\n✅ Tabla 'orders' actualizada correctamente")
    except Exception as e:
        print(f"❌ Error al actualizar la tabla: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    actualizar_tabla_orders()
