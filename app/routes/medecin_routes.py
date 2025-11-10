from flask import Blueprint, render_template

medecin = Blueprint("medecin", __name__, url_prefix="/medecin")

@medecin.route("/dashboard")
def dashboard():
    return render_template("medecin/dashboard.html")

@medecin.route("/patients")
def patients():
    return render_template("medecin/patients.html")

@medecin.route("/chat")
def chat():
    return render_template("medecin/chat.html")

@medecin.route("/profil")
def profil():
    return render_template("medecin/profil.html")

@medecin.route("/disponibilites")
def disponibilites():
    return render_template("medecin/disponibilites.html")

@medecin.route("/statistiques")
def statistiques():
    return render_template("medecin/statistiques.html")

@medecin.route("/rdv_du_jour")
def rdv_du_jour():
    return render_template("medecin/rdv_du_jour.html")

@medecin.route("/agenda")
def agenda():
    return render_template("medecin/agenda.html")

@medecin.route("/avis")
def avis():
    return render_template("medecin/avis.html")
