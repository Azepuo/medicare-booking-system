#!/usr/bin/env python3
"""
Script d'initialisation complète de la base de données
"""

import sys
import os

# Ajouter le répertoire racine au chemin Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from database.connection import test_connection
    from database.migrations.migration_manager import run_all_migrations
    from database.seeders.seeder_manager import run_all_seeders
    print("✅ Modules importés avec succès!")
except ImportError as e:
    print(f" Erreur d'import: {e}")
    print(f" Current dir: {current_dir}")
    print(f" Parent dir: {parent_dir}")
    print(f" Python path: {sys.path}")
    sys.exit(1)

def main():
    print(" Initialisation de la base de données Medicare...")
    print("=" * 50)
    
    # 1. Test de connexion
    print("1. Test de connexion à la base de données...")
    if not test_connection():
        print(" Arrêt: Impossible de se connecter à la base de données")
        return False
    
    # 2. Exécution des migrations
    print("\n2. Application des migrations...")
    if not run_all_migrations():
        print(" Arrêt: Erreur lors des migrations")
        return False
    
    # 3. Exécution des seeders
    print("\n3. Insertion des données de test...")
    if not run_all_seeders():
        print(" Arrêt: Erreur lors de l'insertion des données")
        return False
    
    print("\n" + "=" * 50)
    print(" Base de données initialisée avec succès!")
    print(" Données disponibles:")
    print("   - 10 spécialités médicales")
    print("   - 7 médecins")
    print("   - 8 patients") 
    print("   - 8 rendez-vous de test")
    print("\n L'application est prête à être utilisée!")
    
    return True

if __name__ == "__main__":
    main()