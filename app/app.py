from flask import Flask, render_template
from app.routes.admin_rt.medecin_routes import medecins_bp  # ⬅️ importe ton blueprint (adapter le chemin si besoin)
from app.routes.admin_rt.patient_routes import patients_bp  # ⬅️ importe ton blueprint (adapter le chemin si besoin)

app = Flask(__name__)
app.secret_key = "un_secret_tres_long_et_complexe"  # nécessaire pour flash()

# --- ZAINAB : PARTIE ADMIN GENERALE (hors médecins) --- #

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')




@app.route('/admin/facturation')
def admin_facturation():
    return render_template('admin/facturation.html')


@app.route('/admin/facture_view')
def admin_facture_view():
    return render_template('admin/facture_view.html')


@app.route('/admin/rendez_vous')
def admin_rendez_vous():
    return render_template('admin/rendez_vous.html')


@app.route('/admin/account')
def admin_account():
    return render_template('admin/account.html')


@app.route('/admin/update_admin')
def admin_update_admin():
    return render_template('admin/update_info_admin.html')

# @app.route('/admin/patients')
# def admin_patients():
#     return render_template('admin/patients.html')

# @app.route('/admin/patient_add')
# def admin_patient_add():
#     return render_template('admin/patient_add.html')

# @app.route('/admin/patient_edit')
# def admin_patient_edit():
#     return render_template('admin/patient_edit.html')

@app.route('/admin/facture_add')
def admin_facture_add():
    return render_template('admin/facture_add.html')


@app.route('/admin/rdv_add')
def admin_rdv_add():
    return render_template('admin/rdv_add.html')




@app.route('/admin/rdv_edit')
def admin_rdv_edit():
    return render_template('admin/rdv_edit.html')


@app.route('/admin/facturation_edit')
def admin_facturation_edit():
    return render_template('admin/facturation_edit.html')


# ⚠️ IMPORTANT :
# On supprime les anciennes routes medecins “simples”,
# parce que maintenant c’est le blueprint qui gère tout ça.
# Donc on NE garde PAS :
#   /admin/medecins
#   /admin/medecin_add
#   /admin/medecin_edit
#
# Elles sont remplacées par :
#   /admin/medecins/           -> liste_medecins()
#   /admin/medecins/add        -> ajouter_medecin()
#   /admin/medecins/<id>/edit  -> editer_medecin()
#
# via le blueprint ci-dessous 👇


# --- ENREGISTREMENT DU BLUEPRINT MEDECINS --- #
app.register_blueprint(medecins_bp, url_prefix="/admin/medecins")

app.register_blueprint(patients_bp, url_prefix="/admin/patients")

# --- PARTIE PATIENT (SITE PUBLIC) --- #

@app.route('/')
def accueil():
    return render_template('patient/accueil.html')


@app.route('/medecin')
def dashboard_medecin():
    return "<h1>👨‍⚕️ Dashboard Médecin</h1><p>Espace professionnel en construction...</p><a href='/'>Retour</a>"


@app.route('/prendre-rdv')
def prendre_rdv():
    return "<h1>📅 Prendre Rendez-vous</h1><p>Fonctionnalité à venir...</p><a href='/'>Retour à l'accueil</a>"


@app.route('/medecins')
def liste_medecins_public():
    return "<h1>👨‍⚕️ Liste des Médecins</h1><p>Fonctionnalité à venir...</p><a href='/'>Retour à l'accueil</a>"


@app.route('/mes-rdv')
def mes_rendez_vous():
    return "<h1>📋 Mes Rendez-vous</h1><p>Fonctionnalité à venir...</p><a href='/'>Retour à l'accueil</a>"


if __name__ == '__main__':
    print("🚀 Serveur Flask démarré sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
