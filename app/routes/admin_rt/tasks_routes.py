from flask import Blueprint, request, jsonify, render_template
import xmlrpc.client

tasks_bp = Blueprint('tasks_bp', __name__, url_prefix="/admin/taches")

# ✅ Connexion au serveur RPC
rpc = xmlrpc.client.ServerProxy("http://localhost:8002", allow_none=True)


# ✅ 1️⃣ LISTE DES TÂCHES (Affichage Dashboard)
@tasks_bp.route("/", methods=["GET"])
def liste_taches():
    taches = rpc.liste_taches()
    return render_template("admin/taches.html", taches=taches)


# ✅ 2️⃣ AJOUTER UNE TÂCHE (AJAX)
@tasks_bp.route("/add", methods=["POST"])
def ajouter_tache():
    data = request.get_json()

    titre = data.get("titre")
    statut = data.get("statut")

    if not titre:
        return jsonify({"success": False, "error": "TITRE_OBLIGATOIRE"}), 400

    result = rpc.ajouter_tache({"titre": titre, "statut": statut})

    if result.get("success"):
        return jsonify({"success": True}), 200

    return jsonify({"success": False, "error": "SERVER_ERROR"}), 500


# ✅ 3️⃣ MODIFIER UNE TÂCHE (AJAX)
@tasks_bp.route("/edit/<int:tache_id>", methods=["POST"])
def modifier_tache(tache_id):
    data = request.get_json()
    titre = data.get("titre")
    statut = data.get("statut")

    result = rpc.editer_tache(tache_id, {"titre": titre, "statut": statut})

    if result == True or (isinstance(result, dict) and result.get("success")):
        return jsonify({"success": True}), 200

    return jsonify({"success": False}), 500

# ✅ 4️⃣ SUPPRIMER UNE TÂCHE (AJAX)
@tasks_bp.route("/delete/<int:tache_id>", methods=["POST"])
def supprimer_tache(tache_id):
    result = rpc.supprimer_tache(tache_id)

    if result.get("success"):
        return jsonify({"success": True}), 200

    return jsonify({"success": False}), 500
