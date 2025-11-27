from flask import Blueprint, render_template

patient = Blueprint("patient", __name__, url_prefix="/patient")

@patient.route("/accueil")
def accueil():
    return render_template("patient/accueil.html")

@patient.route("/dashboard")
def dashboard():
    return render_template("patient/dashboard.html")

@patient.route("/mes_rdv")
def mes_rdv():
    return render_template("patient/mes_rdv.html")

@patient.route("/profile")
def profile():
    return render_template("patient/profile.html")

@patient.route("/logout")
def logout():
    return render_template("patient/logout.html")

@patient.route("/prise_rdv")
def prise_rdv():
    return render_template("patient/prise_rdv.html")
