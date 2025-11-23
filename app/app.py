from flask import Flask, render_template
from app.routes.admin_rt.medecin_routes import medecins_bp
from app.routes.admin_rt.patient_routes import patients_bp
from app.routes.admin_rt.rdv_routes import rdv_bp
from app.routes.admin_rt.factures_routes import facture_bp
from app.routes.admin_rt.account_routes import admin_bp

app = Flask(__name__)
app.secret_key = "un_secret_tres_long_et_complexe"


# ✅ Tableau de bord admin
@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')


# ✅ Blueprints Admin
app.register_blueprint(medecins_bp, url_prefix="/admin/medecins")
app.register_blueprint(patients_bp, url_prefix="/admin/patients")
app.register_blueprint(rdv_bp, url_prefix="/admin/rendez_vous")
app.register_blueprint(facture_bp, url_prefix="/admin/facturation")
app.register_blueprint(admin_bp, url_prefix="/admin")


# ✅ Accueil public
@app.route('/')
def accueil():
    return render_template('patient/accueil.html')


if __name__ == '__main__':
    print("🚀 Serveur Flask démarré sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
