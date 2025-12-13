from app.routes.auth_routes import auth
from app.routes.main_routes import main



def register_blueprints(app):
    app.register_blueprint(auth)
    app.register_blueprint(main)
  
    








