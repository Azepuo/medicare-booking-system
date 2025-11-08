from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

#---zainab-----#
@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')
@app.route('/admin/medecins')
def admin_medecins():
    return render_template('admin/medecins.html')
@app.route('/admin/patients')
def admin_patients():
    return render_template('admin/patients.html')
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
@app.route('/admin/patient_add')
def admin_patient_add():
    return render_template('admin/patient_add.html')
@app.route('/admin/medecin_add')
def admin_medecin_add():
    return render_template('admin/medecin_add.html')
@app.route('/admin/facture_add')
def admin_facture_add():
    return render_template('admin/facture_add.html')
@app.route('/admin/rdv_add')
def admin_rdv_add():
    return render_template('admin/rdv_add.html')
@app.route('/admin/patient_edit')
def admin_patient_edit():
    return render_template('admin/patient_edit.html')
@app.route('/admin/medecin_edit')
def admin_medecin_edit():
    return render_template('admin/medecin_edit.html')
@app.route('/admin/rdv_edit')
def admin_rdv_edit():
    return render_template('admin/rdv_edit.html')
@app.route('/admin/facturation_edit')
def admin_facturation_edit():
    return render_template('admin/facturation_edit.html')
#---zainab-----#
# Routes pour l'interface médecin
@app.route('/')
def dashboard():
    return render_template('medecin/dashboard.html')

@app.route('/medecin/dashboard')
def dashboard_medecin():
    return render_template('medecin/dashboard.html')

@app.route('/medecin/patients')
def patients():
    return render_template('medecin/patients.html')

@app.route('/medecin/chat')
def chat():
    return render_template('medecin/chat.html')

@app.route('/medecin/profil')
def profil():
    return render_template('medecin/profil.html')

@app.route('/medecin/disponibilites')
def disponibilites():
    return render_template('medecin/disponibilites.html')

@app.route('/medecin/statistiques')
def statistiques():
    return render_template('medecin/statistiques.html')

@app.route('/medecin/rdv_du_jour')
def rdv_du_jour():
    return render_template('medecin/rdv_du_jour.html')

@app.route('/medecin/agenda')
def agenda():
    return render_template('medecin/agenda.html')

@app.route('/medecin/avis')
def avis():
    return render_template('medecin/avis.html')

# Route pour servir les fichiers statiques
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print(" Serveur Flask démarré sur http://localhost:5000")
    print(" Dashboard: http://localhost:5000/")
    print(" Patients: http://localhost:5000/medecin/patients")
    print(" Chat: http://localhost:5000/medecin/chat")
    print(" Profil: http://localhost:5000/medecin/profil")
    app.run(debug=True, host='0.0.0.0', port=5000)