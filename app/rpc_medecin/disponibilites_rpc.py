# app/rpc_medecin/disponibilites_rpc.py

from flask import Blueprint, request, jsonify
from .disponibilites_rpc_methods import (
    list_disponibilites,
    get_disponibilite,
    create_disponibilite,
    update_disponibilite,
    delete_disponibilite
)

disponibilites_rpc = Blueprint("disponibilites_rpc", __name__, url_prefix="/medecin/rpc/disponibilites")

# ------------------------------------------------------
# LISTE DES DISPONIBILITÉS
# ------------------------------------------------------
@disponibilites_rpc.route("/list", methods=["GET"])
def list_all_dispos():
    try:
        dispos = list_disponibilites()
        return jsonify({"ok": True, "data": dispos})
    except Exception as e:
        print("❌ Erreur list_all_dispos:", e)
        return jsonify({"ok": False, "error": str(e)}), 500

# ------------------------------------------------------
# OBTENIR UNE DISPONIBILITÉ
# ------------------------------------------------------
@disponibilites_rpc.route("/get/<int:dispo_id>", methods=["GET"])
def get_single_dispo(dispo_id):
    try:
        dispo = get_disponibilite(dispo_id)
        if dispo:
            return jsonify({"ok": True, "data": dispo})
        return jsonify({"ok": False, "error": "Disponibilité non trouvée"}), 404
    except Exception as e:
        print("❌ Erreur get_single_dispo:", e)
        return jsonify({"ok": False, "error": str(e)}), 500

# ------------------------------------------------------
# CRÉER UNE DISPONIBILITÉ
# ------------------------------------------------------
@disponibilites_rpc.route("/create", methods=["POST"])
def create_new_dispo():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400

    try:
        new_dispo = create_disponibilite(data)
        return jsonify({"ok": True, "data": new_dispo})
    except Exception as e:
        print("❌ Erreur create_new_dispo:", e)
        return jsonify({"ok": False, "error": str(e)}), 400

# ------------------------------------------------------
# METTRE À JOUR
# ------------------------------------------------------
@disponibilites_rpc.route("/update/<int:dispo_id>", methods=["PUT"])
def update_dispo(dispo_id):
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400

    try:
        updated = update_disponibilite(dispo_id, data)
        if updated:
            return jsonify({"ok": True, "data": updated})
        return jsonify({"ok": False, "error": "Disponibilité non trouvée"}), 404
    except Exception as e:
        print("❌ Erreur update_dispo:", e)
        return jsonify({"ok": False, "error": str(e)}), 400

# ------------------------------------------------------
# SUPPRIMER
# ------------------------------------------------------
@disponibilites_rpc.route("/delete/<int:dispo_id>", methods=["DELETE"])
def delete_dispo_route(dispo_id):
    try:
        success = delete_disponibilite(dispo_id)
        if success:
            return jsonify({"ok": True, "message": "Disponibilité supprimée"})
        return jsonify({"ok": False, "error": "Disponibilité non trouvée"}), 404
    except Exception as e:
        print("❌ Erreur delete_dispo_route:", e)
        return jsonify({"ok": False, "error": str(e)}), 400
