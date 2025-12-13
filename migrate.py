from database.connection import create_connection
from database.migrations.versions import initial_tables

def run_migration():
    conn = create_connection()
    if conn:
        print("🚀 Exécution de la migration...")
        initial_tables.up(conn)          # ✅ on crée
        # NE PAS appeler initial_tables.down(conn) ici
        conn.close()
        print("✅ Migration terminée avec succès !")
    else:
        print("❌ Impossible d'exécuter la migration.")

if __name__ == "__main__":
    run_migration()
