# C:\Users\pc\medicare-db\database\connection.py
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

def get_db_connection():
    """
    Crée et retourne une connexion à la base de données MySQL.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3307)),  # Vérifie le port correct
            database=os.getenv("DB_NAME", "medicare_unified"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "")
        )
        return connection
    except Error as e:
        print(f"Erreur de connexion à la base : {e}")
        return None

def test_connection():
    """
    Teste la connexion à la base de données.
    """
    conn = get_db_connection()
    if conn:
        print("Connexion réussie à la base de données")
        conn.close()
        return True
    else:
        print("Échec de connexion à la base de données")
        return False

if __name__ == "__main__":
    test_connection()
