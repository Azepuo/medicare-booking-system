# Fichier : app/routes/patient_routes.py

from flask import Blueprint, render_template, session, redirect, url_for, flash
# (Assurez-vous que le décorateur login_required est défini ou importé ici)
# from .decorators import login_required 

patient = Blueprint('patient', __name__)

# [NOTE : Vous devez définir le décorateur login_required ici ou l'importer]

@patient.route('/')
def home():
    """Route racine. Redirige si l'utilisateur est connecté."""
    if 'user_id' in session:
        return redirect(url_for('patient.accueil')) # Redirige vers l'accueil du patient si connecté
    return render_template('index.html') # Affiche la page d'accueil publique si déconnecté


@patient.route('/accueil')
# @login_required # Ajoutez ce décorateur pour sécuriser la page
def accueil():
    """Accueil du patient après connexion."""
    return render_template('patient/accueil.html')

# Les autres routes temporaires (/prendre-rdv, /mes-rdv, /medecins) vont ici avec @patient.route
# ...