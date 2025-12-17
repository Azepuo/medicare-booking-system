from flask import Blueprint, request, jsonify
from .patients_rpc_methods import list_patients, get_patient, create_patient, update_patient, delete_patient

patients_rpc = Blueprint("patients_rpc", __name__, url_prefix="/medecin/rpc/patients")

# ------------------------------------------------------
# LISTE DE TOUS LES PATIENTS
# ------------------------------------------------------
@patients_rpc.route("/list", methods=["GET"])
def list_all_patients():
    try:
        patients = list_patients()
        return jsonify({"ok": True, "data": patients})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ------------------------------------------------------
# OBTENIR UN PATIENT
# ------------------------------------------------------
@patients_rpc.route("/get/<int:patient_id>", methods=["GET"])
def get_single_patient(patient_id):
    try:
        patient = get_patient(patient_id)
        if patient:
            return jsonify({"ok": True, "data": patient})
        else:
            return jsonify({"ok": False, "error": "Patient non trouvé"}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ------------------------------------------------------
# CRÉER UN PATIENT
# ------------------------------------------------------
@patients_rpc.route("/create", methods=["POST"])
def create_new_patient():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400
    
    payload = {
        'user_id': data.get('user_id'),  # facultatif
        'nom': data.get('nom'),
        'email': data.get('email'),
        'telephone': data.get('telephone', ''),
        'sexe': data.get('sexe', 'Homme')
    }

    try:
        new_patient = create_patient(payload)
        return jsonify({"ok": True, "data": new_patient})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

# ------------------------------------------------------
# METTRE À JOUR UN PATIENT
# ------------------------------------------------------
@patients_rpc.route("/update/<int:patient_id>", methods=["PUT"])
def update_existing_patient(patient_id):
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400
    
    payload = {key: data[key] for key in ['nom','email','telephone','sexe'] if key in data}

    try:
        updated_patient = update_patient(patient_id, payload)
        if updated_patient:
            return jsonify({"ok": True, "data": updated_patient})
        else:
            return jsonify({"ok": False, "error": "Patient non trouvé"}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

# ------------------------------------------------------
# SUPPRIMER UN PATIENT
# ------------------------------------------------------
@patients_rpc.route("/delete/<int:patient_id>", methods=["DELETE"])
def delete_existing_patient(patient_id):
    try:
        success = delete_patient(patient_id)
        if success:
            return jsonify({"ok": True, "message": "Patient supprimé avec succès"})
        else:
            return jsonify({"ok": False, "error": "Patient non trouvé"}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400
