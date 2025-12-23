from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.disponibilite import Disponibilite
from models.medecin import Medecin

dispo_bp = Blueprint("dispo", __name__)

@dispo_bp.route("/disponibilites/create", methods=["POST"])
def create_disponibilite():

    # 🔐 Vérification authentification
    if "user_id" not in session or session.get("role") != "MEDECIN":
        flash("Non authentifié", "danger")
        return redirect(url_for("auth.login"))

    # 🔁 récupérer le MEDECIN lié au user
    medecin = Medecin.get_by_user_id(session["user_id"])

    if not medecin:
        flash("Médecin introuvable", "danger")
        return redirect(url_for("dashboard"))

    medecin_id = medecin["id"]

    data = {
        "jour_semaine": request.form["jour_semaine"],
        "heure_debut": request.form["heure_debut"],
        "heure_fin": request.form["heure_fin"]
    }

    Disponibilite.create(data, medecin_id)

    flash("Disponibilité ajoutée avec succès", "success")
    return redirect(url_for("dispo.list_disponibilites"))
