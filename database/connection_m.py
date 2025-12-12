import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    """Créer une connexion à la base de données"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            database=os.getenv('DB_NAME', 'medicare_booking'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        return connection
    except Error as e:
        print(f"Erreur de connexion à la base: {e}")
        return None

@contextmanager
def get_cursor():
    """Context manager pour obtenir un curseur MySQL"""
    conn = create_connection()
    if not conn:
        raise RuntimeError("Impossible de se connecter à la base de données")
    try:
        cur = conn.cursor(dictionary=True)
        yield conn, cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def test_connection():
    conn = create_connection()
    if conn:
        print("Connexion à la base réussie")
        conn.close()
        return True
    else:
        print("Échec de connexion à la base")
        return False

if __name__ == "__main__":
    test_connection()
