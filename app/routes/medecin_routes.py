# app/routes/medecin_routes.py
from flask import Blueprint, render_template, jsonify, request
from models.patient import Patient
from models.rendezvous import Rendezvous
from models.medecin import Medecin
from database.connection import create_connection
from datetime import date
from models.disponibilite import Disponibilite
from flask import session

medecin = Blueprint('medecin', __name__)

# ------------------ PAGES ------------------
@medecin.route('/dashboard')
def dashboard():
    return render_template('medecin/dashboard.html')

@medecin.route('/patients')
def patients_page():  # ✅ CORRECT : patients_page
    return render_template('medecin/patients.html')

@medecin.route('/patients/add')
def patient_add_page():
    return render_template('medecin/patient_add.html')

# Dans medecin_routes.py
@medecin.route('/patients/edit/<int:pid>')
def patient_edit_page(pid):
    patient = Patient.get_by_id(pid)
    if not patient:
        return "Patient non trouvé", 404
    return render_template('medecin/patient_edit.html', patient=patient.to_dict())


@medecin.route('/patients/delete/<int:pid>')
def patient_delete_page(pid):
    return render_template('medecin/patient_delete.html', pid=pid)

@medecin.route('/rdv')
def rdv_list():
    return render_template('medecin/rdv_list.html')

@medecin.route('/rdv/add')
def rdv_add_page():
    return render_template('medecin/rdv_add.html')

@medecin.route('/rdv/edit/<int:rid>')
def rdv_edit_page(rid):
    return render_template('medecin/rdv_edit.html', rid=rid)

@medecin.route('/rdv/delete/<int:rid>')
def rdv_delete_page(rid):
    return render_template('medecin/rdv_delete.html', rid=rid)

@medecin.route('/disponibilites')
def dispo_list():
    return render_template('medecin/disponibilites.html')

@medecin.route('/disponibilites/add')
def dispo_add():
    return render_template('medecin/disponibilites_add.html')

@medecin.route('/chat')
def chat():
    return render_template('medecin/chat.html')

@medecin.route('/profil')
def profil():
    return render_template('medecin/profil.html')


# ------------------ API PATIENTS ------------------
@medecin.route('/api/patients', methods=['GET'])
def get_patients_api():
    try:
        patients = Patient.get_all()
        return jsonify([p.to_dict() for p in patients])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient_api(patient_id):
    try:
        p = Patient.get_by_id(patient_id)
        if not p:
            return jsonify({'error': 'Patient non trouvé'}), 404
        return jsonify(p.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/patients', methods=['POST'])
def create_patient_api():
    try:
        data = request.json
        if not data or not data.get('nom') or not data.get('email'):
            return jsonify({'error': 'Nom et email obligatoires'}), 400

        patient = Patient(
            user_id=data.get('user_id'),
            nom=data['nom'],
            email=data['email'],
            telephone=data.get('telephone', ''),
            sexe=data.get('sexe', 'Homme')
        )

        if patient.save():
            return jsonify({'message': 'Patient créé avec succès', 'id': patient.id}), 201
        return jsonify({'error': 'Erreur lors de la création du patient'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient_api(patient_id):
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400

        patient = Patient.get_by_id(patient_id)
        if not patient:
            return jsonify({'error': 'Patient non trouvé'}), 404

        patient.nom = data.get('nom', patient.nom)
        patient.email = data.get('email', patient.email)
        patient.telephone = data.get('telephone', patient.telephone)
        patient.sexe = data.get('sexe', patient.sexe)

        if patient.save():
            return jsonify({'message': 'Patient mis à jour avec succès'})
        return jsonify({'error': 'Erreur mise à jour'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient_api(patient_id):
    try:
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return jsonify({'error': 'Patient non trouvé'}), 404

        if patient.delete():
            return jsonify({'message': 'Patient supprimé avec succès'})
        return jsonify({'error': 'Erreur suppression'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ------------------ API RENDEZ-VOUS ------------------
@medecin.route('/api/rendezvous', methods=['GET'])
def get_rendezvous_api():
    try:
        rdvs = Rendezvous.get_all()
        return jsonify([r.to_dict() for r in rdvs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/rendezvous/today', methods=['GET'])
def get_rendezvous_today_api():
    try:
        today = date.today()
        conn = create_connection()
        if not conn:
            return jsonify({'error': 'Erreur de connexion à la base'}), 500

        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT r.id, r.patient_id, r.medecin_id, r.date_heure, r.statut, r.notes,
                   p.nom AS patient_nom, p.telephone AS patient_telephone,
                   m.nom AS medecin_nom
            FROM rendezvous r
            LEFT JOIN patients p ON r.patient_id = p.id
            LEFT JOIN medecins m ON r.medecin_id = m.id
            WHERE DATE(r.date_heure) = %s
            ORDER BY r.date_heure
        """, (today,))
        rdvs = cur.fetchall()
        cur.close()
        conn.close()

        result = []
        for rdv in rdvs:
            result.append({
                'id': rdv['id'],
                'patient_id': rdv['patient_id'],
                'medecin_id': rdv['medecin_id'],
                'patient_nom': rdv['patient_nom'] or 'N/A',
                'patient_telephone': rdv['patient_telephone'] or 'N/A',
                'medecin_nom': rdv['medecin_nom'] or 'N/A',
                'date_heure': rdv['date_heure'].strftime('%Y-%m-%d %H:%M:%S') if rdv['date_heure'] else '',
                'statut': rdv['statut'] or 'En attente',
                'notes': rdv['notes'] or ''
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
