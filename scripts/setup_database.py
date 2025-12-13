# scripts/setup_database.py

import sys
import os

# Ajout du dossier parent (racine du projet) au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection_p import create_connection
from database.migrations import create_tables
from database.seeders import insert_data


def setup_database():
    """Supprime toutes les anciennes tables, recrée la base, et insère les données de test"""
    conn = create_connection()

    if conn is None:
        print(" Erreur : impossible de se connecter à la base de données.")
        return

    cursor = conn.cursor()

    print("\n Suppression des anciennes tables...")
    create_tables.down(cursor)
    conn.commit()

    print("\n Création des nouvelles tables...")
    create_tables.up(cursor)
    conn.commit()

    print("\n Insertion des données de test...")
    insert_data.seed_all(cursor)
    conn.commit()

    cursor.close()
    conn.close()
    print("\n Base de données initialisée avec succès !")


if __name__ == "__main__":
    setup_database()
