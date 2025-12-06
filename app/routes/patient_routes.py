from flask import Blueprint, render_template
from app.auth_rpc.decorators import role_required

patient = Blueprint("patient", __name__, url_prefix="/patient")

@patient.route("/accueil")
@role_required("patient")
def accueil():
    return render_template("patient/accueil.html")

@patient.route("/dashboard")
@role_required("patient")
def dashboard():
    return render_template("patient/dashboard.html")

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
