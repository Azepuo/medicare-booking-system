from flask import Blueprint, render_template

medecin_bp = Blueprint("medecin", __name__, url_prefix="/medecin")

@medecin_bp.route("/dashboard")
def dashboard():
    return render_template("medecin/dashboard.html")
