# app/routes/__init__.py

from app.routes.authentification.authentification_routes import auth_bp
from app.routes.main_routes import main



def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main)
  
    








