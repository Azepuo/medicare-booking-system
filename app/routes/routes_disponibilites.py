from flask import Blueprint, request, jsonify, session
from models.disponibilite import Disponibilite

dispo = Blueprint('dispo', __name__)

# Vérifier si médecin connecté
def get_current_medecin_id():
    return session.get("medecin_id")  # ⚠ doit être défini lors du login


# ------------------------------
# LISTE DES DISPONIBILITES
# ------------------------------
@dispo.route('/api/disponibilites', methods=['GET'])
def api_get_dispos():
    medecin_id = get_current_medecin_id()
    data = Disponibilite.get_all(medecin_id)
    return jsonify({"success": True, "data": data})


# ------------------------------
# UNE SEULE DISPONIBILITÉ
# ------------------------------
@dispo.route('/api/disponibilites/<int:dispo_id>', methods=['GET'])
def api_get_dispo(dispo_id):
    data = Disponibilite.get_one(dispo_id)
    if not data:
        return jsonify({"success": False, "error": "Disponibilité introuvable"}), 404
    return jsonify({"success": True, "data": data})


# ------------------------------
# AJOUT
# ------------------------------
@dispo.route('/api/disponibilites', methods=['POST'])
def api_add_dispo():
    medecin_id = get_current_medecin_id()
    data = request.json

    if not data:
        return jsonify({"success": False, "error": "Données invalides"}), 400

    new_id = Disponibilite.create(data, medecin_id)
    return jsonify({"success": True, "message": "Disponibilité ajoutée", "id": new_id})


# ------------------------------
# MODIFICATION
# ------------------------------
@dispo.route('/api/disponibilites/<int:dispo_id>', methods=['PUT'])
def api_update_dispo(dispo_id):
    data = request.json
    success = Disponibilite.update(dispo_id, data)

    if not success:
        return jsonify({"success": False, "error": "Modification impossible"}), 400

    return jsonify({"success": True, "message": "Disponibilité modifiée"})


# ------------------------------
# SUPPRESSION
# ------------------------------
@dispo.route('/api/disponibilites/<int:dispo_id>', methods=['DELETE'])
def api_delete_dispo(dispo_id):
    success = Disponibilite.delete(dispo_id)

    if not success:
        return jsonify({"success": False, "error": "Suppression impossible"}), 400

    return jsonify({"success": True, "message": "Disponibilité supprimée"})


# ------------------------------
# STATISTIQUES
# ------------------------------
@dispo.route('/api/disponibilites/stats', methods=['GET'])
def api_dispo_stats():
    medecin_id = get_current_medecin_id()
    stats = Disponibilite.get_stats(medecin_id)

    return jsonify({"success": True, "data": stats})
