# app/rpc_medecin/patients_rpc.py
from flask import Blueprint, request, jsonify
from .patients_rpc_methods import list_patients, get_patient, create_patient, update_patient, delete_patient

patients_rpc = Blueprint("patients_rpc", __name__, url_prefix="/medecin/rpc/patients")

# ------------------------------------------------------
# LISTE DE TOUS LES PATIENTS
# ------------------------------------------------------
@patients_rpc.route("/list", methods=["GET"])
def list_all_patients():
    print("🔍 Route /medecin/rpc/patients/list appelée")
    
    try:
        patients = list_patients()
        print(f"✅ {len(patients)} patients trouvés")
        return jsonify({"ok": True, "data": patients})
        
    except Exception as e:
        print(f"❌ Erreur list_all_patients: {e}")
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
        print(f"❌ Erreur get_single_patient: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

# ------------------------------------------------------
# CRÉER UN PATIENT
# ------------------------------------------------------
@patients_rpc.route("/create", methods=["POST"])
def create_new_patient():
    print("🔍 Route /medecin/rpc/patients/create appelée")
    
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400
    
    try:
        new_patient = create_patient(data)
        return jsonify({"ok": True, "data": new_patient})
    except Exception as e:
        print(f"❌ Erreur create_new_patient: {e}")
        return jsonify({"ok": False, "error": str(e)}), 400

# ------------------------------------------------------
# METTRE À JOUR UN PATIENT
# ------------------------------------------------------
@patients_rpc.route("/update/<int:patient_id>", methods=["PUT"])
def update_existing_patient(patient_id):
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400
    
    try:
        updated_patient = update_patient(patient_id, data)
        if updated_patient:
            return jsonify({"ok": True, "data": updated_patient})
        else:
            return jsonify({"ok": False, "error": "Patient non trouvé"}), 404
    except Exception as e:
        print(f"❌ Erreur update_existing_patient: {e}")
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
        print(f"❌ Erreur delete_existing_patient: {e}")
        return jsonify({"ok": False, "error": str(e)}), 400