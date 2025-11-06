import os
import importlib.util
from database.connection import create_connection

class SeederManager:
    def __init__(self):
        self.seeders_dir = os.path.dirname(__file__)
        self.connection = create_connection()
    
    def run_seeders(self):
        """Exécuter tous les seeders"""
        if not self.connection:
            print("❌ Impossible de se connecter à la base de données")
            return False
        
        try:
            seeder_files = self._get_seeder_files()
            
            for seeder_file in seeder_files:
                print(f"🌱 Exécution du seeder: {seeder_file}")
                if self._run_seeder(seeder_file):
                    print(f"✅ Seeder {seeder_file} exécuté avec succès")
                else:
                    print(f"❌ Échec du seeder {seeder_file}")
                    return False
            
            print("🎉 Tous les seeders ont été exécutés avec succès!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution des seeders: {e}")
            return False
    
    def _get_seeder_files(self):
        """Récupérer la liste des fichiers seeder"""
        seeder_files = []
        if os.path.exists(self.seeders_dir):
            for file in os.listdir(self.seeders_dir):
                if file.endswith('.py') and file not in ['__init__.py', 'seeder_manager.py']:
                    seeder_files.append(file)
        
        # Ordre d'exécution recommandé
        execution_order = [
            'specialites_seeder.py',
            'medecins_seeder.py', 
            'patients_seeder.py',
            'rendezvous_seeder.py'
        ]
        
        # Trier selon l'ordre défini
        ordered_files = []
        for ordered_file in execution_order:
            if ordered_file in seeder_files:
                ordered_files.append(ordered_file)
                seeder_files.remove(ordered_file)
        
        # Ajouter les fichiers restants
        ordered_files.extend(sorted(seeder_files))
        return ordered_files
    
    def _run_seeder(self, seeder_file):
        """Exécuter un seeder spécifique"""
        try:
            spec = importlib.util.spec_from_file_location(
                "seeder", 
                os.path.join(self.seeders_dir, seeder_file)
            )
            seeder_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(seeder_module)
            
            # Exécuter la fonction run() du seeder
            seeder_module.run(self.connection)
            return True
            
        except Exception as e:
            print(f"❌ Erreur dans le seeder {seeder_file}: {e}")
            return False

def run_all_seeders():
    """Fonction utilitaire pour exécuter tous les seeders"""
    manager = SeederManager()
    return manager.run_seeders()