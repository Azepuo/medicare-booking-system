from flask import Blueprint, render_template, request, redirect, url_for, flash
import xmlrpc.client
from datetime import date

facture_bp = Blueprint("facture_bp", __name__)

# ✅ Connexion au serveur RPC
rpc = xmlrpc.client.ServerProxy("http://localhost:8000", allow_none=True)


# ✅ 1️⃣ LISTE DES FACTURES
@facture_bp.route("/", methods=["GET"])
def liste_factures():
    factures = rpc.liste_factures()
    return render_template("admin/facturation.html", factures=factures)


# ✅ 2️⃣ FORMULAIRE POUR CRÉER UNE FACTURE (depuis un RDV)
@facture_bp.route("/create/<int:rdv_id>", methods=["GET", "POST"])
def create_facture(rdv_id):
    if request.method == "POST":
        data = {
            "rdv_id": rdv_id,
            "statut": request.form.get("statut"),
            "moyen_paiement": request.form.get("moyen_paiement"),
            "services": request.form.get("services"),
            "montant_total": request.form.get("montant_total")
        }

        result = rpc.ajouter_facture(data)

        if result.get("success"):
            flash("✅ Facture créée avec succès", "success")
            return redirect(url_for("facture_bp.liste_factures"))

        flash("❌ Erreur lors de la création.", "error")
        return redirect(request.url)

    # GET → afficher formulaire
    rdv = rpc.get_rdv(rdv_id)
    services = rpc.liste_services()
    return render_template(
        "admin/facture_add.html",
        rdv=rdv,
        services=services,
        form_action=url_for("facture_bp.create_facture", rdv_id=rdv_id)
    )



# ✅ 3️⃣ ENREGISTRER LA FACTURE
@facture_bp.route("/store", methods=["POST"])
def store_facture():
    rdv_id = request.form.get("rdv_id")
    statut = request.form.get("statut")
    moyen_paiement = request.form.get("moyen_paiement")

    service_ids = request.form.getlist("service_id[]")
    quantites = request.form.getlist("quantite[]")

    if not service_ids:
        flash("⚠️ Veuillez ajouter au moins un service.", "error")
        return redirect(request.referrer)

    # ✅ 3.1 Créer la facture (retourne facture_id)
    facture_id = rpc.creer_facture({
        "rdv_id": rdv_id,
        "statut": statut,
        "moyen_paiement": moyen_paiement,
        "date_facture": str(date.today())
    })

    # ✅ 3.2 Ajouter les services liés à la facture
    for i in range(len(service_ids)):
        rpc.ajouter_service_facture(
            facture_id,
            int(service_ids[i]),
            int(quantites[i])
        )

    flash("✅ Facture créée avec succès", "success")
    return redirect(url_for("facture_bp.liste_factures"))


# ✅ 4️⃣ AFFICHER LES DÉTAILS D’UNE FACTURE
@facture_bp.route("/details/<int:facture_id>", methods=["GET"])
def details_facture(facture_id):
    facture = rpc.get_facture(facture_id)
    services = rpc.get_services_facture(facture_id)

    if not facture:
        flash("❌ Facture introuvable.", "error")
        return redirect(url_for("facture_bp.liste_factures"))

    return render_template(
        "admin/facture_details.html",
        facture=facture,
        services=services
    )


# ✅ 5️⃣ SUPPRESSION D’UNE FACTURE
@facture_bp.route("/delete/<int:facture_id>", methods=["GET"])
def supprimer_facture(facture_id):
    rpc.supprimer_facture(facture_id)
    flash("✅ Facture supprimée.", "success")
    return redirect(url_for("facture_bp.liste_factures"))
