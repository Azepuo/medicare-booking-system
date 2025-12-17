from flask import Flask, render_template, g, request, url_for
from app.routes.admin_rt.medecin_routes import medecins_bp
from app.routes.admin_rt.patient_routes import patients_bp
from app.routes.admin_rt.rdv_routes import rdv_bp
from app.routes.admin_rt.factures_routes import facture_bp
from app.routes.admin_rt.account_routes import admin_bp
from app.routes.admin_rt.tasks_routes import tasks_bp
from flask import redirect, url_for
import xmlrpc.client
import subprocess
import sys
import os

app = Flask(__name__)
app.secret_key = "un_secret_tres_long_et_complexe"

# ==========================================================
# 🚀 Lancer automatiquement le serveur RPC
# ==========================================================
def start_rpc_server():
    rpc_path = os.path.join(os.getcwd(), "rpc_server_admin.py")

    print(f"🚀 Lancement automatique du serveur RPC : {rpc_path}")

    # Pas de PIPE pour voir les erreurs du RPC dans le terminal
    subprocess.Popen(
        [sys.executable, rpc_path],
        stdout=None,
        stderr=None
    )

# ==========================================================
# 🔗 Connexion au serveur RPC
# ==========================================================
rpc = xmlrpc.client.ServerProxy("http://localhost:8002", allow_none=True)

# ==========================================================
# 📊 Tableau de bord admin
# ==========================================================
@app.route("/admin/dashboard")
def dashboard():
    stats = rpc.get_stats()
    taches = rpc.liste_taches()
    rdv_aujourdhui = rpc.liste_rdv_aujourdhui()

    search = request.args.get("search", "")

    if search:
        rdv_aujourdhui = [
            r for r in rdv_aujourdhui
            if search.lower() in r["patient_nom"].lower()
        ]

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        taches=taches,
        rdv_aujourdhui=rdv_aujourdhui,
        search=search
    )

# ==========================================================
# 📌 Enregistrement des BLUEPRINTS ADMIN
# ==========================================================
app.register_blueprint(medecins_bp, url_prefix="/admin/medecins")
app.register_blueprint(patients_bp, url_prefix="/admin/patients")
app.register_blueprint(rdv_bp, url_prefix="/admin/rendez_vous")
app.register_blueprint(facture_bp, url_prefix="/admin/facturation")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(tasks_bp)

# ==========================================================
# 🌍 Page d’accueil
# ==========================================================
@app.route("/")
def accueil():
    return redirect(url_for("dashboard"))
# ==========================================================
# 🙍 Injecter admin dans tous les templates
# ==========================================================
@app.context_processor
def inject_admin():
    return dict(admin=g.admin)

# ==========================================================
# 🔄 Charger admin avant chaque requête
# ==========================================================
@app.before_request
def load_admin():
    if request.path.startswith("/static"):
        return
    g.admin = rpc.get_admin()

# ==========================================================
# 📊 Injecter les statistiques globales
# ==========================================================
@app.context_processor
def inject_stats():
    return dict(stats=rpc.get_stats())

# ==========================================================
# 🚀 LANCEMENT SERVEUR FLASK
# ==========================================================
if __name__ == "__main__":
    start_rpc_server()  # 🚀 Démarrage automatique du RPC
    print("🔥 Serveur Flask admin démarré sur http://localhost:5001")
    app.run(debug=True, use_reloader=False)
