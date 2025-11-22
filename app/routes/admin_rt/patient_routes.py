# app/routes/patients.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
import xmlrpc.client

patients_bp = Blueprint("patients_bp", __name__)

# Client RPC vers le serveur de services
rpc = xmlrpc.client.ServerProxy("http://localhost:8000", allow_none=True)


# ---------- LISTE DES patients ----------
@patients_bp.route("/", methods=["GET"])
def liste_patients():
    # Récupération via RPC
    patients = rpc.liste_patients()
    # patients est une liste de dicts renvoyée par le serveur RPC
    return render_template("admin/patients.html", patients=patients)


# ---------- FORMULAIRE AJOUT ----------
@patients_bp.route("/add", methods=["GET", "POST"])
def ajouter_patient():
    if request.method == "POST":
        data = {
            "nom": request.form.get("nom"),
            "cin": request.form.get("cin"),
            "email": request.form.get("email"),
            "telephone": request.form.get("telephone"),
            "sexe": request.form.get("sexe"),
            "date_naissance": request.form.get("date_naissance"),
            # "date_inscription": request.form.get("date_inscription") or None,
           }
        rpc.ajouter_patient(data)

        flash("Patient ajouté avec succès", "success")
        return redirect(url_for("patients_bp.liste_patients"))

    # GET → afficher le formulaire
    return render_template("admin/patient_add.html")


# ---------- FORMULAIRE EDIT ----------
@patients_bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
def editer_patient(patient_id):
    # On récupère le médecin via RPC
    patient = rpc.get_patient(patient_id)

    if not patient:
        flash("Médecin introuvable", "error")
        return redirect(url_for("patients_bp.liste_patients"))

    if request.method == "POST":
        data = {
    "nom": request.form.get("nom"),
    "cin": request.form.get("cin"),
    "email": request.form.get("email"),
    "telephone": request.form.get("telephone"),
    "sexe": request.form.get("sexe"),
    "date_naissance": request.form.get("date_naissance"),
}


        rpc.editer_patient(patient_id, data)

        flash("Médecin modifié avec succès", "success")
        return redirect(url_for("patients_bp.liste_patients"))

    # GET → afficher le formulaire pré-rempli
    return render_template("admin/patient_edit.html", patient=patient)


# ---------- SUPPRESSION ----------
@patients_bp.route("/<int:patient_id>/delete", methods=["GET"])
def supprimer_patient(patient_id):
    rpc.supprimer_patient(patient_id)
    flash("Médecin supprimé avec succès", "success")
    return redirect(url_for("patients_bp.liste_patients"))
