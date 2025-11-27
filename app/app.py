from flask import Flask, render_template, g, request
from app.routes.admin_rt.medecin_routes import medecins_bp
from app.routes.admin_rt.patient_routes import patients_bp
from app.routes.admin_rt.rdv_routes import rdv_bp
from app.routes.admin_rt.factures_routes import facture_bp
from app.routes.admin_rt.account_routes import admin_bp
from app.routes.admin_rt.tasks_routes import tasks_bp

import xmlrpc.client

app = Flask(__name__)
app.secret_key = "un_secret_tres_long_et_complexe"

# Connexion RPC
rpc = xmlrpc.client.ServerProxy("http://localhost:8000", allow_none=True)

# Tableau de bord admin
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
    return render_template("admin/dashboard.html", stats=stats, taches=taches, rdv_aujourdhui=rdv_aujourdhui, search=search)

# Blueprints Admin
app.register_blueprint(medecins_bp, url_prefix="/admin/medecins")
app.register_blueprint(patients_bp, url_prefix="/admin/patients")
app.register_blueprint(rdv_bp, url_prefix="/admin/rendez_vous")
app.register_blueprint(facture_bp, url_prefix="/admin/facturation")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(tasks_bp)

# Accueil public
@app.route('/')
def accueil():
    return render_template('patient/accueil.html')

# Rendre admin dispo dans tous les templates
@app.context_processor
def inject_admin():
    return dict(admin=g.admin)

# Charger automatiquement l'admin avant chaque page
@app.before_request
def load_admin():
    # Ne pas executer pour les fichiers statiques
    if request.path.startswith("/static"):
        return
    
    g.admin = rpc.get_admin()

# Statistiques
@app.context_processor
def inject_stats():
    stats = rpc.get_stats()
    return dict(stats=stats)

if __name__ == '__main__':
    print("Serveur Flask demarrage sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
