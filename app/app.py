from flask import Flask, render_template

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
#---zainab-----#
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
def liste_medecins():
    return "<h1>👨‍⚕️ Liste des Médecins</h1><p>Fonctionnalité à venir...</p><a href='/'>Retour à l'accueil</a>"

@app.route('/mes-rdv')
def mes_rendez_vous():
    return "<h1>📋 Mes Rendez-vous</h1><p>Fonctionnalité à venir...</p><a href='/'>Retour à l'accueil</a>"

if __name__ == '__main__':
    print("🚀 Serveur Flask démarré sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)