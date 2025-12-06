from flask import Flask, redirect, url_for
from app.extensions import db, login_manager, bcrypt, socketio
from app.routes import register_blueprints
from app.routes.api_routes import init_api_routes
from app.auth_rpc.rpc_handler import rpc_bp

# Modèles
from models.admin import Admin
from models.medecin import Medecin
from models.patient import Patient


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.secret_key = "votre_cle_secrete"

# 🔹 Configuration SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost:3307/medicare_booking'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app, async_mode="threading")  # important

    # Flask-Login config
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Veuillez vous connecter."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        try:
            role, uid = user_id.split(":")
            uid = int(uid)
            if role == "admin":
                return Admin.get_by_id(uid)
            elif role == "medecin":
                return Medecin.get_by_id(uid)
            elif role == "patient":
                return Patient.get_by_id(uid)
        except Exception as e:
            print("Erreur load_user:", e)
            return None

    # Blueprints
    register_blueprints(app)
    app.register_blueprint(rpc_bp)
    init_api_routes(app)

    @app.route("/")
    def root():
        return redirect(url_for("main.index"))

    return app
