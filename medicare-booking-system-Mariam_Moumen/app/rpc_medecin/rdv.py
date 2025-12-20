# app/rpc_medecin/rdv_rpc.py
from flask import Blueprint, request, jsonify
from .rdv_rpc_methods import list_rdv, get_rdv, create_rdv, update_rdv, delete_rdv
from app.rpc.auth_rpc.auth_rpc import get_user_from_token

rdv_rpc = Blueprint("rdv_rpc", __name__, url_prefix="/medecin/rpc/rdv")

# ----------------- LIST -----------------
@rdv_rpc.route("/list", methods=["GET"])
def list_all_rdvs():
    try:
        user = get_user_from_token()
        if not user or user.get("role") != "MEDECIN":
            return jsonify({"ok": False, "error": "Accès non autorisé"}), 403
        
        user_id = user["user_id"]
        today = request.args.get('today') == '1'
        
        rdvs = list_rdv(user_id, today=today)
        return jsonify({"ok": True, "data": rdvs})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ----------------- GET SINGLE -----------------
@rdv_rpc.route("/get/<int:rdv_id>", methods=["GET"])
def get_single_rdv(rdv_id):
    try:
        user = get_user_from_token()
        if not user or user.get("role") != "MEDECIN":
            return jsonify({"ok": False, "error": "Accès non autorisé"}), 403
        
        user_id = user["user_id"]
        rdv = get_rdv(rdv_id, user_id)
        
        if rdv:
            return jsonify({"ok": True, "data": rdv})
        return jsonify({"ok": False, "error": "Rendez-vous non trouvé"}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ----------------- CREATE -----------------
@rdv_rpc.route("/create", methods=["POST"])
def create_new_rdv():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400

    try:
        user = get_user_from_token()
        if not user or user.get("role") != "MEDECIN":
            return jsonify({"ok": False, "error": "Accès non autorisé"}), 403
        
        user_id = user["user_id"]

        # Validation
        required_fields = ['patient_id', 'date_heure']
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return jsonify({"ok": False, "error": f"Champs requis: {', '.join(missing)}"}), 400

        payload = {
            "user_id": user_id,  # ✅ Directement user_id
            "patient_id": data["patient_id"],
            "date_heure": data["date_heure"],
            "statut": data.get("statut", "En attente"),
            "notes": data.get("notes", "")
        }

        new_rdv = create_rdv(payload)
        return jsonify({"ok": True, "data": new_rdv})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

# ----------------- UPDATE -----------------
@rdv_rpc.route("/update/<int:rdv_id>", methods=["PUT"])
def update_existing_rdv(rdv_id):
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400

    try:
        user = get_user_from_token()
        if not user or user.get("role") != "MEDECIN":
            return jsonify({"ok": False, "error": "Accès non autorisé"}), 403
        
        user_id = user["user_id"]
        
        payload = {k: data[k] for k in ['patient_id','date_heure','statut','notes'] if k in data}
        updated_rdv = update_rdv(rdv_id, user_id, payload)
        
        if updated_rdv:
            return jsonify({"ok": True, "data": updated_rdv})
        return jsonify({"ok": False, "error": "Rendez-vous non trouvé"}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

# ----------------- DELETE -----------------
@rdv_rpc.route("/delete/<int:rdv_id>", methods=["DELETE"])
def delete_existing_rdv(rdv_id):
    try:
        user = get_user_from_token()
        if not user or user.get("role") != "MEDECIN":
            return jsonify({"ok": False, "error": "Accès non autorisé"}), 403
        
        user_id = user["user_id"]
        
        success = delete_rdv(rdv_id, user_id)
        if success:
            return jsonify({"ok": True, "message": "Rendez-vous supprimé"})
        return jsonify({"ok": False, "error": "Rendez-vous non trouvé"}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400