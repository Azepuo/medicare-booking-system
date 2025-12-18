from flask import Blueprint, render_template, request, redirect, url_for, flash
import xmlrpc.client
from datetime import datetime, date

rdv_bp = Blueprint("rdv_bp", __name__)

# ✅ Client RPC
rpc = xmlrpc.client.ServerProxy("http://localhost:8002", allow_none=True)


# =====================================================
# 1️⃣ LISTE DES RDV
# =====================================================
@rdv_bp.route("/", methods=["GET"])
def liste_rdv():
    search = request.args.get("search", "")
    rdvs = rpc.liste_rdv(search)
    return render_template("admin/rendez_vous.html", rdvs=rdvs, search=search)


# =====================================================
# 2️⃣ AJOUT RDV
# =====================================================
@rdv_bp.route("/add", methods=["GET", "POST"])
def ajouter_rdv():
    patients = rpc.liste_patients()
    medecins = rpc.liste_medecins()

    if request.method == "POST":
        date_rdv = request.form.get("date_rdv")
        heure_rdv = request.form.get("heure_rdv")

        if not date_rdv or not heure_rdv:
            flash("⚠️ Date et heure obligatoires.", "error")
            return redirect(request.url)

        # ✅ Fusion date + heure → DATETIME
        date_heure = f"{date_rdv} {heure_rdv}:00"

        # ✅ Bloquer dates passées
        try:
            if datetime.strptime(date_heure, "%Y-%m-%d %H:%M:%S") < datetime.now():
                flash("⚠️ Impossible de choisir une date passée.", "error")
                return redirect(request.url)
        except ValueError:
            flash("⚠️ Format de date invalide.", "error")
            return redirect(request.url)

        data = {
            "patient_id": request.form.get("patient_id"),
            "medecin_id": request.form.get("medecin_id"),
            "date_heure": date_heure,
            "statut": request.form.get("statut") or "en_attente",
            "notes": request.form.get("notes")
        }

        result = rpc.ajouter_rdv(data)

        if isinstance(result, dict) and "error" in result:
            messages = {
                "INACTIVE": "⚠️ Ce médecin n'est pas actif.",
                "NOT_AVAILABLE": "⚠️ Médecin non disponible à cette date/heure.",
                "ALREADY_BOOKED": "⚠️ Ce créneau est déjà réservé (±30 minutes).",
                "MEDECIN_INTROUVABLE": "⚠️ Ce médecin n'existe pas.",
                "FORMAT_DATE_INVALIDE": "⚠️ Format de date invalide.",
                "DATE_HEURE_MANQUANTE": "⚠️ Date et heure sont obligatoires.",
                "ERREUR_BDD": "❌ Erreur lors de l'enregistrement."
            }
            flash(messages.get(result["error"], f"❌ Erreur: {result['error']}"), "error")
            return redirect(request.url)

        flash("✅ Rendez-vous ajouté avec succès", "success")
        return redirect(url_for("rdv_bp.liste_rdv"))

    return render_template(
        "admin/rdv_add.html",
        patients=patients,
        medecins=medecins,
        rdv=None
    )


# =====================================================
# 3️⃣ MODIFIER RDV
# =====================================================
@rdv_bp.route("/<int:rdv_id>/edit", methods=["GET", "POST"])
def editer_rdv(rdv_id):
    rdv = rpc.get_rdv(rdv_id)

    if not rdv:
        flash("❌ Rendez-vous introuvable.", "error")
        return redirect(url_for("rdv_bp.liste_rdv"))

    patients = rpc.liste_patients()
    medecins = rpc.liste_medecins()

    if request.method == "POST":
        date_rdv = request.form.get("date_rdv")
        heure_rdv = request.form.get("heure_rdv")

        if not date_rdv or not heure_rdv:
            flash("⚠️ Date et heure obligatoires.", "error")
            return redirect(request.url)

        date_heure = f"{date_rdv} {heure_rdv}:00"

        if datetime.strptime(date_heure, "%Y-%m-%d %H:%M:%S") < datetime.now():
            flash("⚠️ Impossible de choisir une date passée.", "error")
            return redirect(request.url)

        data = {
            "patient_id": request.form.get("patient_id"),
            "medecin_id": request.form.get("medecin_id"),
            "date_heure": date_heure,
            "statut": request.form.get("statut"),
            "notes": request.form.get("notes")
        }

        result = rpc.editer_rdv(rdv_id, data)

        if isinstance(result, dict) and "error" in result:
            flash("❌ Erreur : " + result["error"], "error")
            return redirect(request.url)

        flash("✅ Rendez-vous modifié avec succès.", "success")
        return redirect(url_for("rdv_bp.liste_rdv"))

    return render_template(
        "admin/rdv_edit.html",
        rdv=rdv,
        patients=patients,
        medecins=medecins
    )


# =====================================================
# 4️⃣ SUPPRESSION RDV
# =====================================================
@rdv_bp.route("/<int:rdv_id>/delete", methods=["GET"])
def supprimer_rdv(rdv_id):
    rpc.supprimer_rdv(rdv_id)
    flash("✅ Rendez-vous supprimé.", "success")
    return redirect(url_for("rdv_bp.liste_rdv"))


# =====================================================
# 5️⃣ DISPONIBILITÉS (AJAX)
# =====================================================
@rdv_bp.route("/dispos/<int:medecin_id>", methods=["GET"])
def disponibilites_medecin(medecin_id):
    return {"dates": rpc.get_disponibilites(medecin_id)}
