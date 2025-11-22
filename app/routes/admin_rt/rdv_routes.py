from flask import Blueprint, render_template, request, redirect, url_for, flash
import xmlrpc.client

rdv_bp = Blueprint("rdv_bp", __name__)

# Client RPC vers le serveur de services
rpc = xmlrpc.client.ServerProxy("http://localhost:8000", allow_none=True)


# ✅ 1️⃣ LISTE DES RENDEZ-VOUS
@rdv_bp.route("/", methods=["GET"])
def liste_rdv():
    rdvs = rpc.liste_rdv()
    return render_template("admin/rendez_vous.html", rdvs=rdvs)


# ✅ 2️⃣ FORMULAIRE AJOUT
@rdv_bp.route("/add", methods=["GET", "POST"])
def ajouter_rdv():
    # Charger patients & médecins pour le select
    patients = rpc.liste_patients()
    medecins = rpc.liste_medecins()

    if request.method == "POST":
        data = {
            "patient_id": request.form.get("patient_id"),
            "medecin_id": request.form.get("medecin_id"),
            "date_rdv": request.form.get("date_rdv"),
            "heure_rdv": request.form.get("heure_rdv"),
            "statut": request.form.get("statut") or "en attente",
            "notes": request.form.get("notes") or None
        }

        rpc.ajouter_rdv(data)
        flash("Rendez-vous ajouté avec succès ✅", "success")
        return redirect(url_for("rdv_bp.liste_rdv"))

    return render_template("admin/rdv_add.html",
                           patients=patients,
                           medecins=medecins)


# ✅ 3️⃣ FORMULAIRE EDITION
@rdv_bp.route("/<int:rdv_id>/edit", methods=["GET", "POST"])
def editer_rdv(rdv_id):
    rdv = rpc.get_rdv(rdv_id)

    if not rdv:
        flash("Rendez-vous introuvable ❌", "error")
        return redirect(url_for("rdv_bp.liste_rdv"))

    patients = rpc.liste_patients()
    medecins = rpc.liste_medecins()

    if request.method == "POST":
        data = {
            "patient_id": request.form.get("patient_id"),
            "medecin_id": request.form.get("medecin_id"),
            "date_rdv": request.form.get("date_rdv"),
            "heure_rdv": request.form.get("heure_rdv"),
            "statut": request.form.get("statut"),
            "notes": request.form.get("notes")
        }

        rpc.editer_rdv(rdv_id, data)
        flash("Rendez-vous modifié avec succès ✅", "success")
        return redirect(url_for("rdv_bp.liste_rdv"))

    return render_template("admin/rdv_edit.html",
                           rdv=rdv,
                           patients=patients,
                           medecins=medecins)


# ✅ 4️⃣ SUPPRESSION
@rdv_bp.route("/<int:rdv_id>/delete", methods=["GET"])
def supprimer_rdv(rdv_id):
    rpc.supprimer_rdv(rdv_id)
    flash("Rendez-vous supprimé ✅", "success")
    return redirect(url_for("rdv_bp.liste_rdv"))
