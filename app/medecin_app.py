from flask import Flask
from app.routes.medecin_routes import medecin_bp

app = Flask(__name__)
app.register_blueprint(medecin_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
