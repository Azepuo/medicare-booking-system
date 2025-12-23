<<<<<<< HEAD
# app/__init__.py
from flask import Flask

# Blueprints
from app.routes.medcin.medecin_routes import medecin
from app.routes.authentification.authentification_routes import auth_bp

# RPC
from app.rpc.auth_rpc.auth_rpc import auth_rpc
=======
from flask import Flask
import mysql.connector

# ✅ Fonction globale accessible depuis "from app import get_db_connection"
def get_db_connection():
    """
    Retourne une connexion à la base de données MySQL
    """
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='medicare_unified'
    )
>>>>>>> Patient_rpc_TM1


def create_app():
    app = Flask(__name__)
<<<<<<< HEAD

    # Configuration
    app.config['SECRET_KEY'] = 'secret123'

    # Enregistrement des blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(auth_rpc)
    app.register_blueprint(medecin, url_prefix='/medecin')

    return app
=======
    app.secret_key = "secret123"
    
    # Configuration MySQL
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'medicare_unified'
    
    # Rendre la fonction accessible depuis l'app également (pour compatibilité)
    app.get_db_connection = get_db_connection
    
    # ✅ ENREGISTRER TOUS LES BLUEPRINTS via la fonction centralisée
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Enregistrer auth_rpc
    from app.rpc.auth_rpc.auth_rpc import auth_rpc
    app.register_blueprint(auth_rpc)
    
    # 📋 AFFICHER LES ROUTES POUR DÉBOGUER
    print("="*70)
    print("📋 ROUTES ENREGISTRÉES:")
    patient_routes_found = False
    for rule in app.url_map.iter_rules():
        route_str = f"  {rule.rule:50} [{', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))}]"
        print(route_str)
        if '/patient/' in rule.rule:
            patient_routes_found = True
    
    print("="*70)
    
    if patient_routes_found:
        print("✅ Routes patient trouvées !")
    else:
        print("❌ AUCUNE route patient trouvée ! Vérifiez register_blueprints()")
    
    print("="*70)
    
    return app
>>>>>>> Patient_rpc_TM1
