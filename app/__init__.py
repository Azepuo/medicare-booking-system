# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'votre-cle-secrete'
    
    # Enregistrement des blueprints
    from app.routes.medcin.medecin_routes import medecin
    app.register_blueprint(medecin, url_prefix='/medecin')
    
    return app