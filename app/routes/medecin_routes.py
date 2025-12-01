from flask import Blueprint

medecin = Blueprint("medecin", __name__, url_prefix="/medecin")

@medecin.route("/")
def home():
    return "Espace médecin en préparation."
