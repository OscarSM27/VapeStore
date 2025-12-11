import pymysql
import hashlib
import os
from pymysql.cursors import DictCursor
from typing import Optional

# DB configuration - usando variables de entorno para seguridad
DB_CONFIG = {
    "host": os.environ.get("DB_HOST"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME", "Vapes"),
    "charset": "utf8mb4",
    "connect_timeout": 10,
    "read_timeout": 10,
    "write_timeout": 10,
    "cursorclass": DictCursor,
}

def get_connection():
    """Devuelve una conexión pymysql usando DB_CONFIG."""
    return pymysql.connect(**DB_CONFIG)

def create_tables():
    """Ejemplo: crea tabla users si no existe (opcional)."""
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(150),
        email VARCHAR(255) UNIQUE,
        password VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    finally:
        conn.close()

def _hash_password(password: str) -> str:
    """Hash simple con sha256. Cambiar a bcrypt en producción."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(name: str, email: str, password: str) -> dict:
    conn = get_connection()
    try:
        hashed = _hash_password(password)
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name, email, hashed))
            user_id = cur.lastrowid
        conn.commit()
        return {"id": user_id, "name": name, "email": email}
    finally:
        conn.close()

def get_user_by_email(email: str) -> Optional[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email=%s LIMIT 1", (email,))
            return cur.fetchone()
    finally:
        conn.close()

if __name__ == "__main__":
    create_tables()
    print("Tablas de ejemplo creadas/verificadas.")