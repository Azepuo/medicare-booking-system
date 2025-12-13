
from app.routes.main_routes import main

<<<<<<< HEAD


=======
try:
    from app.routes.patient_routes import patient
except Exception:
    patient = None
>>>>>>> Patient_rpc_TM
def register_blueprints(app):
    
    app.register_blueprint(main)
  
<<<<<<< HEAD
    








=======
   
    if patient is not None:
        app.register_blueprint(patient)
>>>>>>> Patient_rpc_TM
