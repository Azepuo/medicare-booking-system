
from app.routes.main_routes import main
try:
    from app.routes.patient.patient_routes import patient
except Exception:
    patient = None
def register_blueprints(app):
    
    app.register_blueprint(main)
  
   
    if patient is not None:
        app.register_blueprint(patient)
