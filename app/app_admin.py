from flask import Flask, render_template, request, redirect, g
from app.routes.admin_rt.medecin_routes import medecins_bp
from app.routes.admin_rt.patient_routes import patients_bp
from app.routes.admin_rt.rdv_routes import rdv_bp
from app.routes.admin_rt.factures_routes import facture_bp
from app.routes.admin_rt.account_routes import admin_bp
from app.routes.admin_rt.tasks_routes import tasks_bp


import xmlrpc.client
import jwt
import subprocess
import sys
import os
import time

# ===============================
# CONFIG
# ===============================
app = Flask(__name__)
app.secret_key = "secret123"

SECRET_KEY = "secret123"
LOGIN_URL = "http://127.0.0.1:5000/login"
RPC_URL = "http://localhost:8002"

# ===============================
# 🚀 AUTO START RPC SERVER
# ===============================
def start_rpc_server():
    rpc_file = os.path.join(os.getcwd(), "rpc_server_admin.py")
    subprocess.Popen([sys.executable, rpc_file])
    time.sleep(1)  # laisser le temps au RPC de démarrer

start_rpc_server()

# ===============================
# RPC CLIENT
# ===============================
rpc = xmlrpc.client.ServerProxy(RPC_URL, allow_none=True)

# ===============================
# 🔐 AUTH SIMPLE (JWT)
# ===============================
@app.before_request
def load_user():
    g.user_id = None
    g.role = None
    g.admin = None

    if request.path.startswith("/static"):
        return

    token = request.cookies.get("access_token")
    if not token:
        return

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        g.user_id = payload.get("user_id")
        g.role = payload.get("role")

        if g.role == "ADMIN":
            try:
                g.admin = rpc.get_admin()
            except Exception:
                g.admin = None

    except Exception:
        pass

# ===============================
# 🌍 GLOBALS TEMPLATES
# ===============================
@app.context_processor
def inject_globals():
    return dict(
        admin=g.admin,
        user_id=g.user_id,
        role=g.role
    )

@app.context_processor
def inject_stats():
    try:
        return dict(stats=rpc.get_stats())
    except Exception:
        return dict(stats={
            "total_medecins": 0,
            "total_patients": 0,
            "rdv_aujourd_hui": 0
        })

# ===============================
# 📊 DASHBOARD ADMIN
# ===============================
@app.route("/admin/dashboard")
def dashboard():

    if not g.user_id or g.role != "ADMIN":
        return redirect(LOGIN_URL)

    try:
        stats = rpc.get_stats()
        taches = rpc.liste_taches()
        rdv_aujourdhui = rpc.liste_rdv_aujourdhui()
    except Exception:
        stats = {}
        taches = []
        rdv_aujourdhui = []

    search = request.args.get("search", "")
    if search:
        rdv_aujourdhui = [
            r for r in rdv_aujourdhui
            if search.lower() in r.get("patient_nom", "").lower()
        ]

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        taches=taches,
        rdv_aujourdhui=rdv_aujourdhui,
        search=search
    )

# ===============================
# BLUEPRINTS
# ===============================
app.register_blueprint(medecins_bp, url_prefix="/admin/medecins")
app.register_blueprint(patients_bp, url_prefix="/admin/patients")
app.register_blueprint(rdv_bp, url_prefix="/admin/rendez_vous")
app.register_blueprint(facture_bp, url_prefix="/admin/facturation")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(tasks_bp)

# ===============================
# START
# ===============================
if __name__ == "__main__":
    print("🔥 Admin → http://127.0.0.1:5003/admin/dashboard")
    app.run(port=5003, debug=True)
