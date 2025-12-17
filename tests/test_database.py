# tests/test_database.py
import sys
import os

# Ajoute le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from app.database.connection_p import create_connection
    from app.models.medecin import Medecin
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("💡 Essayons avec des chemins relatifs...")
    try:
        # Essaye avec des imports relatifs
        from database.connection import create_connection
        from models.medecin import Medecin
    except ImportError:
        print("❌ Impossible de charger les modules")
        sys.exit(1)

def test_database():
    print("🧪 Test de la base de données...")
    
    # Test de connexion
    connection = create_connection()
    if connection:
        print("✅ Connexion à la base de données réussie!")
        connection.close()
    else:
        print("❌ Échec de connexion à la base de données")
        return
    
    # Test des modèles
    medecins = Medecin.get_all()
    print(f"📊 Nombre de médecins dans la base: {len(medecins)}")
    
    if len(medecins) == 0:
        print("💡 La base est vide - tu peux ajouter des données de test")
    else:
        for medecin in medecins:
            print(f"   - {medecin.nom} ({medecin.specialite})")

if __name__ == "__main__":
    test_database()