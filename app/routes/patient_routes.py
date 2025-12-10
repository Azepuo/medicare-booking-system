from flask import Blueprint, render_template, make_response # 💡 CORRECTION: Ajoutez make_response
from app.auth_rpc.decorators import role_required

patient = Blueprint("patient", __name__, url_prefix="/patient")

@patient.route("/accueil")
@role_required("patient")
def accueil():
    return render_template("patient/accueil.html")

@patient.route("/dashboard")
@role_required("patient")
def dashboard():
    # 1. Création d'un objet réponse
    response = make_response(render_template("patient/dashboard.html"))
    
    # 2. Ajout des en-têtes pour DÉSACTIVER le cache du navigateur
    # C'est ce qui corrige la boucle de redirection après logout.
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # 3. Retourne l'objet réponse modifié
    return response

@patient.route("/mes_rdv")
@role_required("patient")
def mes_rdv():
    return render_template("patient/mes_rdv.html")

@patient.route("/profile")
@role_required("patient")
def profile():
    return render_template("patient/profile.html")

@patient.route("/logout")
@role_required("patient")
def logout():
    return render_template("patient/logout.html")


@patient.route("/prise_rdv")
@role_required("patient")
def prise_rdv():
    return render_template("patient/prise_rdv.html")
