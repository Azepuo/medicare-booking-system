from flask import Flask
from app.routes.medecin_routes import medecin_bp
from app.rpc.auth_rpc.auth_rpc import auth_rpc

app = Flask(__name__)
app.register_blueprint(medecin_bp, url_prefix="/medecin")
app.register_blueprint(auth_rpc)

if __name__ == "__main__":
    app.run(port=5002, debug=True)
