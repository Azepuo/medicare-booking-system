from app.routes.patient_routes import patient_bp
from flask import Flask

def create_patient_app():
    app = Flask(__name__)
    app.secret_key = "secret123"
    app.register_blueprint(patient_bp)
    return app

if __name__ == "__main__":
    app = create_patient_app()
    app.run(debug=True, port=5001)
