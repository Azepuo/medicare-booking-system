# app/__init__.py
from flask import Flask

# Blueprints
from app.routes.medcin.medecin_routes import medecin
from app.routes.authentification.authentification_routes import auth_bp

# RPC
from app.rpc.auth_rpc.auth_rpc import auth_rpc


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'secret123'

    # Enregistrement des blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(auth_rpc)
    app.register_blueprint(medecin, url_prefix='/medecin')

    return app
