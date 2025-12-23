# app/rpc_medecin/rdv_rpc.py
from flask import Blueprint, request, jsonify
from .rdv_rpc_methods import list_rdv, get_rdv, create_rdv, update_rdv, delete_rdv
from app.rpc.auth_rpc.auth_rpc import get_user_from_token
from database.connection import create_connection

rdv_rpc = Blueprint("rdv_rpc", __name__, url_prefix="/medecin/rpc/rdv")

def get_medecin_id_from_user_id(user_id):
    """Récupérer l'ID du médecin à partir du user_id"""
    conn = create_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM medecins WHERE user_id = %s", (user_id,))
        medecin = cursor.fetchone()
        
        if medecin:
            return medecin['id']
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération du médecin: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn:
            conn.close()

# ----------------- LIST -----------------
@rdv_rpc.route("/list", methods=["GET"])
def list_all_rdvs():
    try:
        user = get_user_from_token()
        if not user or user.get("role") != "MEDECIN":
            return jsonify({"ok": False, "error": "Accès non autorisé"}), 403
        
        # Récupérer le medecin_id à partir du user_id
        medecin_id = get_medecin_id_from_user_id(user["user_id"])
        if not medecin_id:
            return jsonify({"ok": False, "error": "Médecin non trouvé"}), 404
        
        today = request.args.get('today') == '1'
        
        rdvs = list_rdv(medecin_id, today=today)
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
        
        medecin_id = get_medecin_id_from_user_id(user["user_id"])
        if not medecin_id:
            return jsonify({"ok": False, "error": "Médecin non trouvé"}), 404
        
        rdv = get_rdv(rdv_id, medecin_id)
        
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
        
        medecin_id = get_medecin_id_from_user_id(user["user_id"])
        if not medecin_id:
            return jsonify({"ok": False, "error": "Médecin non trouvé"}), 404

        # Validation
        required_fields = ['patient_id', 'date_heure']
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return jsonify({"ok": False, "error": f"Champs requis: {', '.join(missing)}"}), 400

        payload = {
            "medecin_id": medecin_id,
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
        
        medecin_id = get_medecin_id_from_user_id(user["user_id"])
        if not medecin_id:
            return jsonify({"ok": False, "error": "Médecin non trouvé"}), 404
        
        payload = {k: data[k] for k in ['patient_id','date_heure','statut','notes'] if k in data}
        updated_rdv = update_rdv(rdv_id, medecin_id, payload)
        
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
        
        medecin_id = get_medecin_id_from_user_id(user["user_id"])
        if not medecin_id:
            return jsonify({"ok": False, "error": "Médecin non trouvé"}), 404
        
        success = delete_rdv(rdv_id, medecin_id)
        if success:
            return jsonify({"ok": True, "message": "Rendez-vous supprimé"})
        return jsonify({"ok": False, "error": "Rendez-vous non trouvé"}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400