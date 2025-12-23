# app/seed.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.seeders import insert_data
import mysql.connector

def main():
    # ⚡ Connexion à la base de données
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '3306'),  # vérifie le port correct
        database=os.getenv('DB_NAME', 'medicare_unified'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '')
    )
    cursor = connection.cursor()

    try:
        insert_data.seed_all(connection, cursor)  # ⚡ passer connection ET cursor
        print("Toutes les données ont été insérées avec succès !")
    except Exception as e:
        print("Erreur lors de l'insertion des données :", e)
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()
