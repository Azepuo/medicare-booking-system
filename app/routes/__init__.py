from app.routes.auth_routes import auth
from app.routes.main_routes import main
from app.routes.admin_routes import admin
from app.routes.medecin_routes import medecin
try:
    from app.routes.patient_routes import patient
except Exception:
    patient = None


def register_blueprints(app):
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(medecin)
    if patient is not None:
        app.register_blueprint(patient)








