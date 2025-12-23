# app/__init__.py
from flask import Flask
import mysql.connector

# ==============================
# DB CONNECTION (GLOBAL)
# ==============================
def get_db_connection():
    """
    Retourne une connexion MySQL
    """
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='medicare_unified'
    )

# ==============================
# APP FACTORY
# ==============================
def create_app():
    app = Flask(__name__)

    # 🔐 SECRET KEY
    app.config['SECRET_KEY'] = 'secret123'

    # 📦 Config DB (optionnel mais propre)
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'medicare_unified'

    # Rendre la connexion accessible via app
    app.get_db_connection = get_db_connection

    # ==============================
    # BLUEPRINTS
    # ==============================
    from app.routes import register_blueprints
    register_blueprints(app)

    # RPC AUTH
    from app.rpc.auth_rpc.auth_rpc import auth_rpc
    app.register_blueprint(auth_rpc)

    # ==============================
    # DEBUG ROUTES (OPTIONNEL)
    # ==============================
    print("=" * 60)
    print("📋 ROUTES ENREGISTRÉES :")
    for rule in app.url_map.iter_rules():
        print(f"{rule.rule:45} {list(rule.methods)}")
    print("=" * 60)

    return app
