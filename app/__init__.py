from flask import Flask
from .extensions import db, login_manager, bcrypt

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ton_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialisation des extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Enregistrement des blueprints
    from .routes.auth_routes import auth
    app.register_blueprint(auth)

    from .routes.admin_routes import admin
    app.register_blueprint(admin, url_prefix='/admin')

    from .routes.patient_routes import patient
    app.register_blueprint(patient, url_prefix='/patient')

    from .routes.medecin_routes import medecin
    app.register_blueprint(medecin, url_prefix='/medecin')

    from .routes.main_routes import main
    app.register_blueprint(main)  # accueil, services, about

    return app
