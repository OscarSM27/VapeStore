"""
Conexión y funciones para la tabla `productos`.
Usa get_connection() desde db/main.py (que ya tiene la configuración).
"""
import os
import sys

# asegurar que la raíz del proyecto esté en sys.path (carpeta que contiene 'db')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pymysql
from typing import List, Dict, Tuple, Any

# IMPORTA get_connection desde el paquete db (db/main.py)
from db.main import get_connection

def init_db() -> None:
    sql_create = """
    CREATE TABLE IF NOT EXISTS productos (
        id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
        codigo VARCHAR(100) UNIQUE,
        marca VARCHAR(150) NOT NULL,
        sabor VARCHAR(150),
        tipo VARCHAR(50),
        stock INT DEFAULT 0,
        precio DECIMAL(10,2) DEFAULT 0.00,
        descripcion TEXT,
        image_url VARCHAR(512),
        thumb_url VARCHAR(512),
        image_thumb_url VARCHAR(512),
        image_name VARCHAR(255),
        image_size INT,
        image_mime VARCHAR(50),
        image_uploaded_at TIMESTAMP NULL,
        fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        activo TINYINT(1) DEFAULT 1
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql_create)
            # intentamos añadir columnas adicionales si faltan (ignoramos errores)
            alters = [
                "ALTER TABLE productos ADD COLUMN thumb_url VARCHAR(512);",
                "ALTER TABLE productos ADD COLUMN image_thumb_url VARCHAR(512);",
                "ALTER TABLE productos ADD COLUMN image_url VARCHAR(512);",
                "ALTER TABLE productos ADD COLUMN image_name VARCHAR(255);",
                "ALTER TABLE productos ADD COLUMN image_size INT;",
                "ALTER TABLE productos ADD COLUMN image_mime VARCHAR(50);",
                "ALTER TABLE productos ADD COLUMN image_uploaded_at TIMESTAMP NULL;"
            ]
            for s in alters:
                try:
                    cur.execute(s)
                except Exception:
                    pass
        conn.commit()
    finally:
        conn.close()

def _get_table_columns(conn: pymysql.connections.Connection, table_name: str) -> set:
    sql = """
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
    """
    with conn.cursor() as cur:
        cur.execute(sql, (table_name,))
        rows = cur.fetchall()
    return {r["COLUMN_NAME"] for r in rows}

def insertar_producto(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Inserta solo las columnas que existan en la tabla `productos`.
    Evita errores 1054 si las columnas tienen nombres distintos (p.ej. thumb_url).
    """
    conn = get_connection()
    try:
        cols = _get_table_columns(conn, "productos")
        candidates = [
            "codigo", "marca", "sabor", "tipo", "stock", "precio", "descripcion",
            "image_url", "thumb_url", "image_thumb_url", "image_name", "image_size", "image_mime", "image_uploaded_at"
        ]
        insert_cols = []
        values = []
        for c in candidates:
            if c in cols:
                insert_cols.append(c)
                if c == "stock":
                    values.append(int(data.get("stock") or 0))
                elif c == "precio":
                    values.append(float(data.get("precio") or 0.0))
                elif c == "image_size":
                    v = data.get("image_size")
                    values.append(int(v) if v is not None else None)
                else:
                    # permitir que data tenga keys image_thumb_url o thumb_url según lo que se setee en GUI
                    values.append(data.get(c))
        if "marca" not in insert_cols:
            return False, "Columna 'marca' no encontrada en la tabla productos."

        placeholders = ", ".join(["%s"] * len(insert_cols))
        cols_sql = ", ".join(f"`{c}`" for c in insert_cols)
        sql = f"INSERT INTO productos ({cols_sql}) VALUES ({placeholders})"
        with conn.cursor() as cur:
            cur.execute(sql, tuple(values))
        conn.commit()
        return True, "Producto agregado"
    except pymysql.err.IntegrityError as e:
        return False, f"Error de integridad: {e}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def listar_productos(limit: int = 200) -> List[Dict[str, Any]]:
    sql = "SELECT * FROM productos ORDER BY fecha_ingreso DESC LIMIT %s"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()
    finally:
        conn.close()