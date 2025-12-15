#C:\Users\pc\medicare-db\app\__init__.py
from flask import Flask
from app.routes.authentification.authentification_routes import auth_bp
from app.rpc.auth_rpc.auth_rpc import auth_rpc

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret123"

    # enregistrer les blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(auth_rpc)  # ← ajouter cette ligne !

    return app


