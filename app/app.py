from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

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
    print("🚀 Serveur Flask démarré sur http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/")
    print("👥 Patients: http://localhost:5000/medecin/patients")
    print("💬 Chat: http://localhost:5000/medecin/chat")
    print("👤 Profil: http://localhost:5000/medecin/profil")
    app.run(debug=True, host='0.0.0.0', port=5000)