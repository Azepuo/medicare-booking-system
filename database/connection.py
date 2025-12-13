import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    """Créer une connexion à la base de données"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '3306'),
            database=os.getenv('DB_NAME', 'db_m'),
            ## admin database=os.getenv('DB_NAME', 'medicare'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        return connection
    except Error as e:
        print(f" Erreur de connexion à la base: {e}")
        return None

def test_connection():
    """Tester la connexion à la base de données"""
    conn = create_connection()
    if conn:
        print(" Connexion à la base de données réussie")
        conn.close()
        return True
    else:
        print(" Échec de connexion à la base de données")
        return False

if __name__ == "__main__":
    test_connection()