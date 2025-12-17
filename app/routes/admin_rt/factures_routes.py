from flask import Blueprint, render_template, request, redirect, url_for, flash
import xmlrpc.client
from datetime import date

facture_bp = Blueprint("facture_bp", __name__, url_prefix="/admin/facturation")

# ✅ Connexion RPC
rpc = xmlrpc.client.ServerProxy("http://localhost:8002", allow_none=True)


# ✅ 1️⃣ LISTE DES FACTURES
@facture_bp.route("/", methods=["GET"])
def liste_factures():
    search = request.args.get("search", "")
    factures = rpc.liste_factures(search)
    return render_template("admin/facturation.html", factures=factures, search=search)


# ✅ 2️⃣ AJOUT D'UNE FACTURE
@facture_bp.route("/create/<int:rdv_id>", methods=["GET", "POST"])
def create_facture(rdv_id):

    # ✅ POST → Enregistrer
    if request.method == "POST":
        data = {
            "rdv_id": rdv_id,
            "statut": request.form.get("statut"),
            "moyen_paiement": request.form.get("moyen_paiement"),
            "services": request.form.get("services"),
            "montant_total": request.form.get("montant_total"),
            "date_facture": str(date.today())
        }

        result = rpc.ajouter_facture(data)

        if result.get("success"):
            flash("✅ Facture créée avec succès", "success")
            return redirect(url_for("facture_bp.liste_factures"))

        flash("❌ Erreur lors de la création.", "error")
        return redirect(request.url)

    # ✅ GET → Afficher formulaire
    rdv = rpc.get_rdv(rdv_id)
    services = rpc.liste_services()

    return render_template(
        "admin/facture_add.html",
        rdv=rdv,
        services=services,
        form_action=url_for("facture_bp.create_facture", rdv_id=rdv_id)
    )



# ✅ 3️⃣ ÉDITION D'UNE FACTURE
@facture_bp.route("/edit/<int:facture_id>", methods=["GET", "POST"])
def edit_facture(facture_id):

    # ✅ POST → Enregistrer modifications
    if request.method == "POST":
        data = {
            "statut": request.form.get("statut"),
            "moyen_paiement": request.form.get("moyen_paiement"),
            "services": request.form.get("services"),
            "montant_total": request.form.get("montant_total")
        }

        result = rpc.editer_facture(facture_id, data)

        if result.get("success"):
            flash("✅ Facture modifiée avec succès", "success")
            return redirect(url_for("facture_bp.liste_factures"))

        flash("❌ Erreur lors de la modification.", "error")
        return redirect(request.url)

    # ✅ GET → Charger la facture + services
    facture = rpc.get_facture(facture_id)
    services = rpc.liste_services()

    if not facture:
        flash("❌ Facture introuvable.", "error")
        return redirect(url_for("facture_bp.liste_factures"))

    return render_template(
        "admin/facture_edit.html",
        facture=facture,
        services=services,
        form_action=url_for("facture_bp.edit_facture", facture_id=facture_id)
    )



# ✅ 4️⃣ VISUALISATION
@facture_bp.route("/details/<int:facture_id>")
def details_facture(facture_id):
    facture = rpc.get_facture(facture_id)
    services_facture = rpc.get_services_facture(facture_id)   # ✅ NOUVEAU
    services_all = rpc.liste_services()                       # ✅ NOUVEAU

    if not facture:
        flash("❌ Facture introuvable.", "error")
        return redirect(url_for("facture_bp.liste_factures"))

    return render_template(
        "admin/facture_view.html",
        facture=facture,
        services=services_facture,
        services_all=services_all
    )




# ✅ 5️⃣ SUPPRESSION
@facture_bp.route("/delete/<int:facture_id>")
def supprimer_facture(facture_id):
    rpc.supprimer_facture(facture_id)
    flash("✅ Facture supprimée.", "success")
    return redirect(url_for("facture_bp.liste_factures"))


