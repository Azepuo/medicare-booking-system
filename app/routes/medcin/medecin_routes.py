# app/routes/medecin_routes.py
from flask import Blueprint, render_template, jsonify, request
from models.patient import Patient
from models.rendezvous import Rendezvous
from models.medecin import Medecin
from database.connection_m import create_connection  # ✅ AJOUTEZ CET IMPORT
from datetime import datetime, date
from models.disponibilite import Disponibilite
from flask import session


medecin = Blueprint('medecin', __name__)

# ------------------ PAGES ------------------
@medecin.route('/dashboard')
def dashboard():
    return render_template('medecin/dashboard.html')

@medecin.route('/patients')
def patients():
    return render_template('medecin/patients.html')

@medecin.route('/patients/add')
def patient_add_page():
    return render_template('medecin/patient_add.html')

@medecin.route('/patients/edit/<int:pid>')
def patient_edit_page(pid):
    return render_template('medecin/patient_edit.html', pid=pid)

@medecin.route('/patients/delete/<int:pid>')
def patient_delete_page(pid):
    return render_template('medecin/patient_delete.html', pid=pid)

# ------------------ RENDEZ-VOUS PAGES ------------------
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

# ---------------- LISTE DES DISPONIBILITÉS ----------------
@medecin.route("/disponibilites")
def dispo_list():
    return render_template("medecin/disponibilites.html")  # correspond au fichier réel

# ---------------- AJOUT D’UNE DISPONIBILITÉ ----------------
@medecin.route("/disponibilites/add")
def dispo_add():
    return render_template("medecin/disponibilites_add.html")  # correspond au fichier réel



@medecin.route('/chat')
def chat():
    return render_template('medecin/chat.html')

@medecin.route('/profil')
def profil():
    return render_template('medecin/profil.html')

# ------------------ API ROUTES ------------------
# Routes API pour les patients
@medecin.route('/api/patients', methods=['GET'])
def get_patients():
    """Récupérer tous les patients"""
    try:
        patients = Patient.get_all()
        patients_data = []
        for p in patients:
            patients_data.append({
                'id': p.id,
                'nom': p.nom,
                'email': p.email,
                'telephone': p.telephone,
                'date_inscription': str(p.date_inscription) if p.date_inscription else None
            })
        return jsonify(patients_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Récupérer un patient par ID"""
    try:
        patient = Patient.get_by_id(patient_id)
        if patient:
            return jsonify({
                'id': patient.id,
                'nom': patient.nom,
                'email': patient.email,
                'telephone': patient.telephone,
                'date_inscription': str(patient.date_inscription) if patient.date_inscription else None
            })
        return jsonify({'error': 'Patient non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/patients', methods=['POST'])
def create_patient():
    """Créer un nouveau patient"""
    try:
        data = request.json
        
        if not data.get('nom') or not data.get('email'):
            return jsonify({'error': 'Nom et email sont obligatoires'}), 400
        
        patient = Patient(
            nom=data['nom'],
            email=data['email'],
            telephone=data.get('telephone', '')
        )
        
        if patient.save():
            return jsonify({
                'message': 'Patient créé avec succès',
                'id': patient.id,
                'patient': {
                    'id': patient.id,
                    'nom': patient.nom,
                    'email': patient.email,
                    'telephone': patient.telephone
                }
            }), 201
        else:
            return jsonify({'error': 'Erreur lors de la création du patient'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Mettre à jour un patient"""
    try:
        data = request.json
        patient = Patient.get_by_id(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient non trouvé'}), 404
        
        if 'nom' in data:
            patient.nom = data['nom']
        if 'email' in data:
            patient.email = data['email']
        if 'telephone' in data:
            patient.telephone = data['telephone']
        
        if patient.save():
            return jsonify({
                'message': 'Patient mis à jour avec succès',
                'patient': {
                    'id': patient.id,
                    'nom': patient.nom,
                    'email': patient.email,
                    'telephone': patient.telephone
                }
            })
        else:
            return jsonify({'error': 'Erreur lors de la mise à jour'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Supprimer un patient"""
    try:
        patient = Patient.get_by_id(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient non trouvé'}), 404
        
        if patient.delete():
            return jsonify({'message': 'Patient supprimé avec succès'})
        else:
            return jsonify({'error': 'Erreur lors de la suppression'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ API ROUTES POUR LES RENDEZ-VOUS ------------------
@medecin.route('/api/rendezvous', methods=['GET'])
def get_rendezvous():
    """Récupérer tous les rendez-vous"""
    try:
        rendezvous = Rendezvous.get_all()
        rendezvous_data = []
        for r in rendezvous:
            rendezvous_data.append({
                'id': r.id,
                'patient_id': r.patient_id,
                'patient_nom': r.patient_nom,
                'medecin_id': r.medecin_id,
                'medecin_nom': r.medecin_nom,
                'date_heure': str(r.date_heure) if r.date_heure else None,
                'statut': r.statut,
                'notes': r.notes
            })
        return jsonify(rendezvous_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/rendezvous/today', methods=['GET'])
def get_rendezvous_today():
    """Récupérer les rendez-vous d'aujourd'hui"""
    try:
        today = date.today()
        
        conn = create_connection()  # ✅ MAINTENANT create_connection EST IMPORTÉ
        if not conn:
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
            
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT r.*, p.nom AS patient_nom, p.telephone AS patient_telephone, 
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

@medecin.route('/api/rendezvous/<int:rdv_id>', methods=['GET'])
def get_rendezvous_by_id(rdv_id):
    """Récupérer un rendez-vous par ID"""
    try:
        rdv = Rendezvous.get_by_id(rdv_id)
        if rdv:
            return jsonify({
                'id': rdv.id,
                'patient_id': rdv.patient_id,
                'patient_nom': rdv.patient_nom,
                'medecin_id': rdv.medecin_id,
                'medecin_nom': rdv.medecin_nom,
                'date_heure': str(rdv.date_heure) if rdv.date_heure else None,
                'statut': rdv.statut,
                'notes': rdv.notes
            })
        return jsonify({'error': 'Rendez-vous non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/rendezvous', methods=['POST'])
def create_rendezvous():
    """Créer un nouveau rendez-vous"""
    try:
        data = request.json
        
        # Validation des données
        if not data.get('patient_id') or not data.get('date_heure'):
            return jsonify({'error': 'patient_id et date_heure sont obligatoires'}), 400
        
        # Utiliser l'ID du médecin connecté (pour l'instant on utilise 1)
        medecin_id = data.get('medecin_id', 1)
        
        rdv = Rendezvous(
            patient_id=data['patient_id'],
            medecin_id=medecin_id,
            date_heure=data['date_heure'],
            statut=data.get('statut', 'En attente'),
            notes=data.get('notes', '')
        )
        
        if rdv.save():
            return jsonify({
                'message': 'Rendez-vous créé avec succès',
                'id': rdv.id,
                'rendezvous': {
                    'id': rdv.id,
                    'patient_id': rdv.patient_id,
                    'medecin_id': rdv.medecin_id,
                    'date_heure': rdv.date_heure,
                    'statut': rdv.statut,
                    'notes': rdv.notes
                }
            }), 201
        else:
            return jsonify({'error': 'Erreur lors de la création du rendez-vous'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/rendezvous/<int:rdv_id>', methods=['PUT'])
def update_rendezvous(rdv_id):
    """Mettre à jour un rendez-vous"""
    try:
        data = request.json
        rdv = Rendezvous.get_by_id(rdv_id)
        
        if not rdv:
            return jsonify({'error': 'Rendez-vous non trouvé'}), 404
        
        # Mettre à jour les champs
        if 'date_heure' in data:
            rdv.date_heure = data['date_heure']
        if 'statut' in data:
            rdv.statut = data['statut']
        if 'notes' in data:
            rdv.notes = data['notes']
        
        if rdv.save():
            return jsonify({
                'message': 'Rendez-vous mis à jour avec succès',
                'rendezvous': {
                    'id': rdv.id,
                    'patient_id': rdv.patient_id,
                    'medecin_id': rdv.medecin_id,
                    'date_heure': rdv.date_heure,
                    'statut': rdv.statut,
                    'notes': rdv.notes
                }
            })
        else:
            return jsonify({'error': 'Erreur lors de la mise à jour'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/rendezvous/<int:rdv_id>', methods=['DELETE'])
def delete_rendezvous(rdv_id):
    """Supprimer un rendez-vous"""
    try:
        rdv = Rendezvous.get_by_id(rdv_id)
        
        if not rdv:
            return jsonify({'error': 'Rendez-vous non trouvé'}), 404
        
        if rdv.delete():
            return jsonify({'message': 'Rendez-vous supprimé avec succès'})
        else:
            return jsonify({'error': 'Erreur lors de la suppression'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500