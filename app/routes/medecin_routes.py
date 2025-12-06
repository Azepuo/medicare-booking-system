from flask import Blueprint, render_template
from app.auth_rpc.decorators import role_required

medecin = Blueprint("medecin", __name__, url_prefix="/medecin")

# 🔹 Dashboard
@medecin.route("/dashboard")
@role_required("medecin")
def dashboard():
    return render_template("medecin/dashboard.html")

# 🔹 Gestion des patients
@medecin.route("/patients")
@role_required("medecin")
def patients():
    return render_template("medecin/patients.html")

# 🔹 Chat
@medecin.route("/chat")
@role_required("medecin")
def chat():
    return render_template("medecin/chat.html")

# 🔹 Profil
@medecin.route("/profil")
@role_required("medecin")
def profil():
    return render_template("medecin/profil.html")

# 🔹 Disponibilités
@medecin.route("/disponibilites")
@role_required("medecin")
def disponibilites():
    return render_template("medecin/disponibilites.html")

# 🔹 Statistiques
@medecin.route("/statistiques")
@role_required("medecin")
def statistiques():
    return render_template("medecin/statistiques.html")

# 🔹 Rendez-vous du jour
@medecin.route("/rdv_du_jour")
@role_required("medecin")
def rdv_du_jour():
    return render_template("medecin/rdv_du_jour.html")

# 🔹 Agenda
@medecin.route("/agenda")
@role_required("medecin")
def agenda():
    return render_template("medecin/agenda.html")

# 🔹 Avis
@medecin.route("/avis")
@role_required("medecin")
def avis():
    return render_template("medecin/avis.html")
