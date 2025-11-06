import os
import importlib.util
from database.connection import create_connection

class MigrationManager:
    def __init__(self):
        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'versions')
        self.connection = create_connection()
    
    def get_applied_migrations(self):
        """Récupérer la liste des migrations appliquées"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            
            # Créer la table de suivi des migrations si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("SELECT name FROM migrations ORDER BY applied_at")
            applied = [row[0] for row in cursor.fetchall()]
            return applied
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des migrations: {e}")
            return []
    
    def run_migrations(self):
        """Exécuter toutes les migrations non appliquées"""
        if not self.connection:
            print("❌ Impossible de se connecter à la base de données")
            return False
        
        try:
            applied_migrations = self.get_applied_migrations()
            migration_files = self._get_migration_files()
            
            for migration_file in migration_files:
                if migration_file not in applied_migrations:
                    print(f"🔄 Application de la migration: {migration_file}")
                    if self._run_migration(migration_file):
                        self._mark_migration_applied(migration_file)
                        print(f"✅ Migration {migration_file} appliquée avec succès")
                    else:
                        print(f"❌ Échec de la migration {migration_file}")
                        return False
            
            print("🎉 Toutes les migrations ont été appliquées avec succès!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution des migrations: {e}")
            return False
    
    def _get_migration_files(self):
        """Récupérer la liste des fichiers de migration"""
        migration_files = []
        if os.path.exists(self.migrations_dir):
            for file in os.listdir(self.migrations_dir):
                if file.endswith('.py') and file != '__init__.py':
                    migration_files.append(file)
        
        # Trier par nom (qui contient le numéro de version)
        migration_files.sort()
        return migration_files
    
    def _run_migration(self, migration_file):
        """Exécuter une migration spécifique"""
        try:
            # Importer dynamiquement le module de migration
            spec = importlib.util.spec_from_file_location(
                "migration", 
                os.path.join(self.migrations_dir, migration_file)
            )
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)
            
            # Exécuter la fonction up() de la migration
            migration_module.up(self.connection)
            return True
            
        except Exception as e:
            print(f"❌ Erreur dans la migration {migration_file}: {e}")
            return False
    
    def _mark_migration_applied(self, migration_file):
        """Marquer une migration comme appliquée"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO migrations (name) VALUES (%s)", (migration_file,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur lors du marquage de la migration: {e}")
            return False

def run_all_migrations():
    """Fonction utilitaire pour exécuter toutes les migrations"""
    manager = MigrationManager()
    return manager.run_migrations()