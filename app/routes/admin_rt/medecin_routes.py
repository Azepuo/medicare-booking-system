from flask import Blueprint, render_template, request, redirect, url_for, flash
import xmlrpc.client

medecins_bp = Blueprint("medecins_bp", __name__)

# 🔗 Client RPC
rpc = xmlrpc.client.ServerProxy("http://localhost:8000", allow_none=True)

# =====================================================
# 📋 LISTE DES MEDECINS
# =====================================================
@medecins_bp.route("/", methods=["GET"])
def liste_medecins():
    search = request.args.get("search", "")
    medecins = rpc.liste_medecins(search)

    return render_template(
        "admin/medecins.html",
        medecins=medecins,
        search=search
    )

# =====================================================
# ➕ AJOUT MEDECIN
# =====================================================
@medecins_bp.route("/add", methods=["GET", "POST"])
def ajouter_medecin():
    if request.method == "POST":
        data = {
            "nom_complet": request.form.get("nom_complet"),  # ✅ Changez "nom" en "nom_complet"
            "email": request.form.get("email"),
            "telephone": request.form.get("telephone"),
            "id_specialisation": request.form.get("id_specialisation"),
            "tarif_consultation": request.form.get("tarif_consultation") or None,
            "statut": request.form.get("statut", "Actif"),
        }
        
        result = rpc.ajouter_medecin(data)
        
        flash(
            f"Médecin ajouté avec succès. Mot de passe temporaire : {result['generated_password']}",
            "success"
        )
        return redirect(url_for("medecins_bp.liste_medecins"))
    
    specialisations = rpc.liste_specialisations()
    return render_template(
        "admin/medecin_add.html",
        specialisations=specialisations
    )

# =====================================================
# ✏️ EDITER MEDECIN
# =====================================================
@medecins_bp.route("/<int:medecin_id>/edit", methods=["GET", "POST"])
def editer_medecin(medecin_id):
    medecin = rpc.get_medecin(medecin_id)

    if not medecin:
        flash("Médecin introuvable", "error")
        return redirect(url_for("medecins_bp.liste_medecins"))

    if request.method == "POST":
        data = {
            "nom": request.form.get("nom_complet"),
            "email": request.form.get("email"),
            "telephone": request.form.get("telephone"),
            "id_specialisation": request.form.get("id_specialisation"),
            "tarif_consultation": request.form.get("tarif_consultation") or None,
            "statut": request.form.get("statut"),
        }

        rpc.editer_medecin(medecin_id, data)
        flash("Médecin modifié avec succès", "success")
        return redirect(url_for("medecins_bp.liste_medecins"))

    # 🔥 spécialités pour le select
    specialisations = rpc.liste_specialisations()

    return render_template(
        "admin/medecin_edit.html",
        medecin=medecin,
        specialisations=specialisations
    )

# =====================================================
# 🗑️ SUPPRIMER MEDECIN
# =====================================================
@medecins_bp.route("/<int:medecin_id>/delete", methods=["GET"])
def supprimer_medecin(medecin_id):
    rpc.supprimer_medecin(medecin_id)
    flash("Médecin supprimé avec succès", "success")
    return redirect(url_for("medecins_bp.liste_medecins"))
