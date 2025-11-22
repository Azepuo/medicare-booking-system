# app/routes/medecins.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
import xmlrpc.client

medecins_bp = Blueprint("medecins_bp", __name__)

# Client RPC vers le serveur de services
rpc = xmlrpc.client.ServerProxy("http://localhost:8000", allow_none=True)


# ---------- LISTE DES MEDECINS ----------
@medecins_bp.route("/", methods=["GET"])
def liste_medecins():
    # Récupération via RPC
    medecins = rpc.liste_medecins()
    # medecins est une liste de dicts renvoyée par le serveur RPC
    return render_template("admin/medecins.html", medecins=medecins)


# ---------- FORMULAIRE AJOUT ----------
@medecins_bp.route("/add", methods=["GET", "POST"])
def ajouter_medecin():
    if request.method == "POST":
        data = {
            "nom": request.form.get("nom_complet"),
            "email": request.form.get("email"),
            "telephone": request.form.get("telephone"),
            "specialite": request.form.get("specialite"),
            "annees_experience": request.form.get("annees_experience") or None,
            "tarif_consultation": request.form.get("tarif_consultation") or None,
            "description": request.form.get("description"),
            "statut": request.form.get("statut"),
        }

        rpc.ajouter_medecin(data)

        flash("Médecin ajouté avec succès", "success")
        return redirect(url_for("medecins_bp.liste_medecins"))

    # GET → afficher le formulaire
    return render_template("admin/medecin_add.html")


# ---------- FORMULAIRE EDIT ----------
@medecins_bp.route("/<int:medecin_id>/edit", methods=["GET", "POST"])
def editer_medecin(medecin_id):
    # On récupère le médecin via RPC
    medecin = rpc.get_medecin(medecin_id)

    if not medecin:
        flash("Médecin introuvable", "error")
        return redirect(url_for("medecins_bp.liste_medecins"))

    if request.method == "POST":
        data = {
            "nom": request.form.get("nom_complet"),
            "email": request.form.get("email"),
            "telephone": request.form.get("telephone"),
            "specialite": request.form.get("specialite"),
            "annees_experience": request.form.get("annees_experience") or None,
            "tarif_consultation": request.form.get("tarif_consultation") or None,
            "description": request.form.get("description"),
            "statut": request.form.get("statut"),
        }

        rpc.editer_medecin(medecin_id, data)

        flash("Médecin modifié avec succès", "success")
        return redirect(url_for("medecins_bp.liste_medecins"))

    # GET → afficher le formulaire pré-rempli
    return render_template("admin/medecin_edit.html", medecin=medecin)


# ---------- SUPPRESSION ----------
@medecins_bp.route("/<int:medecin_id>/delete", methods=["GET"])
def supprimer_medecin(medecin_id):
    rpc.supprimer_medecin(medecin_id)
    flash("Médecin supprimé avec succès", "success")
    return redirect(url_for("medecins_bp.liste_medecins"))
