from flask import Flask
from app.routes import register_blueprints
from app.routes.api_routes import init_api_routes
import subprocess
import sys
import os
# ==========================================================
# 🚀 Lancer automatiquement le serveur RPC Patient
# ==========================================================
def start_rpc_server():
    rpc_path = os.path.join(os.getcwd(), "server_rpc_Patient.py")

    print(f"🚀 Lancement automatique du serveur RPC Patient : {rpc_path}")

    # Popen sans PIPE pour afficher les logs du serveur RPC dans le terminal
    subprocess.Popen(
        [sys.executable, rpc_path],
        stdout=None,
        stderr=None
    )


# ==========================================================
# 📦 Fonction de création de l'application Flask
# ==========================================================
def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.secret_key = "votre_cle_secrete"

    # Register blueprints (auth, main, admin, medecin, patient)
    register_blueprints(app)

    # Register API routes (non-blueprint simple functions)
    init_api_routes(app)

    @app.route("/")
    def root():
        from flask import redirect, url_for
        return redirect(url_for("main.index"))

    return app


# ==========================================================
# 🚀 LANCEMENT SERVEUR FLASK + RPC AUTOMATIQUE
# ==========================================================
if __name__ == "__main__":
    start_rpc_server()  # <-- lancement auto du RPC Patient

    app = create_app()
    print("🔥 Patient App running: http://localhost:5005")
    app.run(debug=True, host="0.0.0.0", port=5005)
