from database.connection_m import create_connection
from database.migrations.create_tables import up, down

def migrate():
    conn = create_connection()
    if not conn:
        print("Erreur : impossible de se connecter à la base de données")
        return
    cur = conn.cursor()
    try:
        # Supprimer les anciennes tables si nécessaire
        down(cur)
        # Créer les tables
        up(cur)
        conn.commit()
        print("Migration réussie ! Toutes les tables ont été créées.")
    except Exception as e:
        conn.rollback()
        print("Erreur lors de la migration :", e)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
