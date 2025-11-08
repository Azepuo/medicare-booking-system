from flask import Flask, render_template
app = Flask(__name__)

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

# Lancer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)
