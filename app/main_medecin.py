from flask import Flask

# Blueprints "pages"
from app.routes.medcin.medecin_routes import medecin

# Blueprints RPC
from app.rpc_medecin.disponibilites_rpc import disponibilites_rpc

# Routes disponibilités (normal)

from app.rpc.auth_rpc.auth_rpc import auth_rpc
from app.routes.authentification.authentification_routes import auth_bp
from app.routes.main_routes import main

def create_app():
    app = Flask(__name__)
    app.secret_key = "SECRET_KEY"

    # ========== Enregistrement des blueprints ==========
    app.register_blueprint(medecin, url_prefix="/medecin")

    # Blueprint RPC (pas de prefix : c’est direct /rpc/…)
    app.register_blueprint(disponibilites_rpc)

    # Blueprint des Disponibilités normales
   

    # Importez le blueprint RP
    app.register_blueprint(auth_rpc)
# Enregistrez-le





    app.register_blueprint(auth_bp)
    app.register_blueprint(main)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True,port=5002)  # Port 5002 pour éviter conflit avec d'autres services
