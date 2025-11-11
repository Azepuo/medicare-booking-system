from flask import Flask,send_from_directory




app = Flask(__name__)

# --- Enregistrement des Blueprints ---


# --- Route d'accueil globale ---


# --- Fichiers statiques ---
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)
from flask import Flask, render_template
app = Flask(__name__)

# la brache mes rendez-vous pour patient routes
# Route pour la page d'accueil
@app.route('/')
def accueil():
    return render_template('patient/accueil.html')
# Route pour le dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('patient/dashboard.html')
# Route pour mes rendez-vous
@app.route('/mes_rdv')
def mes_rdv():
    return render_template('patient/mes_rdv.html')
# Route pour le profil
@app.route('/profile')
def profile():
    return render_template('patient/profile.html')
@app.route('/logout')
def logout():
    return render_template('patient/logout.html')
@app.route('/prise_rdv')
def priverdv():
    return render_template('patient/prise_rdv.html')
#fin de la brache mes rendez-vous pour patient routes



# --- Lancement du serveur ---
if __name__ == '__main__':
 
    print("🏠 Accueil: http://localhost:5000/\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
