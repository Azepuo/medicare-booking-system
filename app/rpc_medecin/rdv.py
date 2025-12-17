# app/rpc_medecin/rdv_rpc.py

from flask import Blueprint, request, jsonify
from . import rdv_rpc_methods   # Import correct depuis le même dossier

rdv_rpc = Blueprint("rdv_rpc", __name__, url_prefix="/medecin/rpc/rdv")


# ------------------------------------------------------
# LISTE DE TOUS LES RDV
# ------------------------------------------------------
@rdv_rpc.route("/list", methods=["GET"])
def list_all_rdv():
    data = rdv_rpc_methods.list_all_rdv()
    return jsonify({"ok": True, "data": data})


# ------------------------------------------------------
# LISTE DES RDV D'AUJOURD'HUI
# ------------------------------------------------------
@rdv_rpc.route("/today", methods=["GET"])
def list_today_rdv():
    data = rdv_rpc_methods.list_today_rdv()
    return jsonify({"ok": True, "data": data})


# ------------------------------------------------------
# OBTENIR UN RDV
# ------------------------------------------------------
@rdv_rpc.route("/get/<int:rid>", methods=["GET"])
def get_single_rdv(rid):
    rdv = rdv_rpc_methods.get_rdv(rid)
    if not rdv:
        return jsonify({"ok": False, "error": "Rendez-vous non trouvé"}), 404
    return jsonify({"ok": True, "data": rdv})


# ------------------------------------------------------
# CRÉER UN RDV
# ------------------------------------------------------
@rdv_rpc.route("/create", methods=["POST"])
def create_new_rdv():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400
    try:
        new_rdv = rdv_rpc_methods.create_rdv(data)
        return jsonify({"ok": True, "data": new_rdv})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ------------------------------------------------------
# METTRE À JOUR UN RDV
# ------------------------------------------------------
@rdv_rpc.route("/update/<int:rid>", methods=["PUT"])
def update_existing_rdv(rid):
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400
    try:
        updated = rdv_rpc_methods.update_rdv(rid, data)
        return jsonify({"ok": True, "data": updated})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ------------------------------------------------------
# SUPPRIMER UN RDV
# ------------------------------------------------------
@rdv_rpc.route("/delete/<int:rid>", methods=["DELETE"])
def delete_existing_rdv(rid):
    try:
        ok = rdv_rpc_methods.delete_rdv(rid)
        if not ok:
            return jsonify({"ok": False, "error": "Rendez-vous non trouvé"}), 404
        return jsonify({"ok": True, "message": "Rendez-vous supprimé avec succès"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400
