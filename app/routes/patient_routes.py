from flask import Blueprint

patient = Blueprint("patient", __name__, url_prefix="/patient")

@patient.route("/")
def home():
    return "Espace patient en préparation."
