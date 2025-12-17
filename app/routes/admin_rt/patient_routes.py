from flask import Blueprint, render_template, request, redirect, url_for, flash
import xmlrpc.client

patients_bp = Blueprint("patients_bp", __name__)
rpc = xmlrpc.client.ServerProxy("http://localhost:8002", allow_none=True)

# ======================
# LISTE DES PATIENTS
# ======================
@patients_bp.route("/", methods=["GET"])
def liste_patients():
    search = request.args.get("search", "")
    patients = rpc.liste_patients(search)
    return render_template(
        "admin/patients.html",
        patients=patients,
        search=search
    )

# ======================
# AJOUT PATIENT (ADMIN)
# ======================
@patients_bp.route("/add", methods=["GET", "POST"])
def ajouter_patient():
    if request.method == "POST":
        data = {
            "nom": request.form.get("nom"),
            "email": request.form.get("email"),
            "telephone": request.form.get("telephone"),
            "sexe": request.form.get("sexe")
        }

        result = rpc.ajouter_patient(data)

        # 🔐 mot de passe généré côté serveur RPC
        if result.get("success"):
            flash(
                f"Patient ajouté avec succès. "
                f"Mot de passe généré : {result['generated_password']}",
                "success"
            )
        else:
            flash("Erreur lors de l’ajout du patient", "error")

        return redirect(url_for("patients_bp.liste_patients"))

    return render_template("admin/patient_add.html")

# ======================
# MODIFIER PATIENT
# ======================
@patients_bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
def editer_patient(patient_id):
    patient = rpc.get_patient(patient_id)

    if not patient:
        flash("Patient introuvable", "error")
        return redirect(url_for("patients_bp.liste_patients"))

    if request.method == "POST":
        data = {
            "nom": request.form.get("nom"),
            "email": request.form.get("email"),
            "telephone": request.form.get("telephone"),
            "sexe": request.form.get("sexe")
        }

        rpc.editer_patient(patient_id, data)
        flash("Patient modifié avec succès", "success")
        return redirect(url_for("patients_bp.liste_patients"))

    return render_template(
        "admin/patient_edit.html",
        patient=patient
    )

# ======================
# SUPPRIMER PATIENT
# ======================
@patients_bp.route("/<int:patient_id>/delete", methods=["GET"])
def supprimer_patient(patient_id):
    rpc.supprimer_patient(patient_id)
    flash("Patient supprimé avec succès", "success")
    return redirect(url_for("patients_bp.liste_patients"))
