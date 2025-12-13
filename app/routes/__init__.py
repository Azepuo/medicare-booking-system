from app.routes.main_routes import main

try:
    from app.routes.patient_routes import patient
except ImportError:
    patient = None


def register_blueprints(app):
    # Blueprint principal
    app.register_blueprint(main)

    # Blueprint patient (optionnel)
    if patient:
        app.register_blueprint(patient)
