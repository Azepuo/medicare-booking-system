from flask import Blueprint, render_template, request, redirect, url_for, flash
import xmlrpc.client
from datetime import date

rdv_bp = Blueprint("rdv_bp", __name__)

# ✅ Client RPC
rpc = xmlrpc.client.ServerProxy("http://localhost:8000", allow_none=True)


# ✅ 1️⃣ LISTE DES RDV
@rdv_bp.route("/", methods=["GET"])
def liste_rdv():
    search = request.args.get("search", "")
    rdvs = rpc.liste_rdv(search)
    return render_template("admin/rendez_vous.html", rdvs=rdvs, search=search)


# ✅ 2️⃣ AJOUT D’UN RDV
@rdv_bp.route("/add", methods=["GET", "POST"])
def ajouter_rdv():
    patients = rpc.liste_patients()
    medecins = rpc.liste_medecins()

    if request.method == "POST":
        data = {
            "patient_id": request.form.get("patient_id"),
            "medecin_id": request.form.get("medecin_id"),
            "date_rdv": request.form.get("date_rdv"),
            "heure_rdv": request.form.get("heure_rdv"),
            "statut": request.form.get("statut") or "en_attente",
            "notes": request.form.get("notes")
        }

        # ✅ Bloquer les dates passées
        if data["date_rdv"] < str(date.today()):
            flash("⚠️ Impossible de choisir une date passée.", "error")
            return redirect(url_for("rdv_bp.ajouter_rdv"))

        # ✅ Envoi au RPC
        result = rpc.ajouter_rdv(data)

        # ✅ Gestion des erreurs
        if isinstance(result, dict) and "error" in result:
            if result["error"] == "INACTIVE":
                flash("⚠️ Ce médecin n'est pas actif.", "error")
            elif result["error"] == "ON_LEAVE":
                flash("⚠️ Ce médecin est en congé.", "error")
            elif result["error"] == "NOT_AVAILABLE":
                flash("⚠️ Le médecin n'est pas disponible à cette date/heure.", "error")
            elif result["error"] == "ALREADY_BOOKED":
                flash("⚠️ Ce créneau est déjà réservé.", "error")
            else:
                flash("❌ Erreur inconnue.", "error")

            return redirect(url_for("rdv_bp.ajouter_rdv"))

        flash("✅ Rendez-vous ajouté avec succès", "success")
        return redirect(url_for("rdv_bp.liste_rdv"))

    return render_template(
        "admin/rdv_add.html",
        patients=patients,
        medecins=medecins,
        rdv=None,
        form_action=url_for("rdv_bp.ajouter_rdv")
    )


# ✅ 3️⃣ MODIFICATION D’UN RDV
from datetime import datetime, date

@rdv_bp.route("/<int:rdv_id>/edit", methods=["GET", "POST"])
def editer_rdv(rdv_id):
    rdv = rpc.get_rdv(rdv_id)

    if not rdv:
        flash("❌ Rendez-vous introuvable.", "error")
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

        # ✅ Vérifier date vide
        if not data["date_rdv"]:
            flash("⚠️ La date est obligatoire.", "error")
            return redirect(request.url)

        # ✅ Conversion date
        date_rdv_obj = datetime.strptime(data["date_rdv"], "%Y-%m-%d").date()

        # ✅ Empêcher dates passées
        if date_rdv_obj < date.today():
            flash("⚠️ Impossible de choisir une date passée.", "error")
            return redirect(request.url)

        # ✅ RPC
        result = rpc.editer_rdv(rdv_id, data)

        if isinstance(result, dict) and "error" in result:
            flash("❌ Erreur : " + result["error"], "error")
            return redirect(request.url)

        flash("✅ Rendez-vous modifié avec succès.", "success")
        return redirect(url_for("rdv_bp.liste_rdv"))

    return render_template(
        "admin/rdv_edit.html",   # ✅ Le bon template !
        rdv=rdv,
        patients=patients,
        medecins=medecins,
        form_action=url_for("rdv_bp.editer_rdv", rdv_id=rdv_id)
    )



# ✅ 4️⃣ SUPPRESSION
@rdv_bp.route("/<int:rdv_id>/delete", methods=["GET"])
def supprimer_rdv(rdv_id):
    rpc.supprimer_rdv(rdv_id)
    flash("✅ Rendez-vous supprimé.", "success")
    return redirect(url_for("rdv_bp.liste_rdv"))


# ✅ 5️⃣ API JS – DISPONIBILITÉS
@rdv_bp.route("/dispos/<int:medecin_id>", methods=["GET"])
def disponibilites_medecin(medecin_id):
    dates = rpc.get_disponibilites(medecin_id)
    return {"dates": dates}
