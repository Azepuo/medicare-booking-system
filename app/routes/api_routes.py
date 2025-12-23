from flask import jsonify, request
from models.patientp import Patient
from models.rendezvousp import RendezVous
from models.medecinp import Medecin

def init_api_routes(app):
    
    # ==================== PATIENTS ====================
    
    @app.route('/api/patients', methods=['GET'])
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
    
    @app.route('/api/patients/<int:patient_id>', methods=['GET'])
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
    
    @app.route('/api/patients', methods=['POST'])
    def create_patient():
        """Créer un nouveau patient"""
        try:
            data = request.json
            
            # Validation des données
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
    
    @app.route('/api/patients/<int:patient_id>', methods=['PUT'])
    def update_patient(patient_id):
        """Mettre à jour un patient"""
        try:
            data = request.json
            patient = Patient.get_by_id(patient_id)
            
            if not patient:
                return jsonify({'error': 'Patient non trouvé'}), 404
            
            # Mettre à jour les champs
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
    
    @app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
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
    
    # ==================== MÉDECINS ====================
    
    @app.route('/api/medecins', methods=['GET'])
    def get_medecins():
        """Récupérer tous les médecins"""
        try:
            medecins = Medecin.get_all()
            medecins_data = []
            for m in medecins:
                medecins_data.append({
                    'id': m.id,
                    'nom': m.nom,
                    'specialite': m.specialite,
                    'email': m.email,
                    'annees_experience': m.annees_experience,
                    'tarif_consultation': float(m.tarif_consultation) if m.tarif_consultation else None,
                    'description': m.description
                })
            return jsonify(medecins_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/medecins/<int:medecin_id>', methods=['GET'])
    def get_medecin(medecin_id):
        """Récupérer un médecin par ID"""
        try:
            medecin = Medecin.get_by_id(medecin_id)
            if medecin:
                return jsonify({
                    'id': medecin.id,
                    'nom': medecin.nom,
                    'specialite': medecin.specialite,
                    'email': medecin.email,
                    'annees_experience': medecin.annees_experience,
                    'tarif_consultation': float(medecin.tarif_consultation) if medecin.tarif_consultation else None,
                    'description': medecin.description
                })
            return jsonify({'error': 'Médecin non trouvé'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/medecins/specialite/<string:specialite>', methods=['GET'])
    def get_medecins_by_specialite(specialite):
        """Récupérer les médecins par spécialité"""
        try:
            medecins = Medecin.get_by_specialite(specialite)
            medecins_data = []
            for m in medecins:
                medecins_data.append({
                    'id': m.id,
                    'nom': m.nom,
                    'specialite': m.specialite,
                    'email': m.email,
                    'annees_experience': m.annees_experience,
                    'tarif_consultation': float(m.tarif_consultation) if m.tarif_consultation else None,
                    'description': m.description
                })
            return jsonify(medecins_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== RENDEZ-VOUS ====================
    
    @app.route('/api/rendezvous', methods=['GET'])
    def get_rendezvous():
        """Récupérer tous les rendez-vous avec détails"""
        try:
            rendezvous = RendezVous.get_all()
            rendezvous_data = []
            for r in rendezvous:
                rendezvous_data.append({
                    'id': r.id,
                    'patient_id': r.patient_id,
                    'patient_nom': getattr(r, 'patient_nom', ''),
                    'medecin_id': r.medecin_id,
                    'medecin_nom': getattr(r, 'medecin_nom', ''),
                    'date_heure': str(r.date_heure) if r.date_heure else None,
                    'statut': r.statut,
                    'notes': r.notes
                })
            return jsonify(rendezvous_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/rendezvous/<int:rdv_id>', methods=['GET'])
    def get_rendezvous_by_id(rdv_id):
        """Récupérer un rendez-vous par ID"""
        try:
            rdv = RendezVous.get_by_id(rdv_id)
            if rdv:
                return jsonify({
                    'id': rdv.id,
                    'patient_id': rdv.patient_id,
                    'patient_nom': getattr(rdv, 'patient_nom', ''),
                    'medecin_id': rdv.medecin_id,
                    'medecin_nom': getattr(rdv, 'medecin_nom', ''),
                    'date_heure': str(rdv.date_heure) if rdv.date_heure else None,
                    'statut': rdv.statut,
                    'notes': rdv.notes
                })
            return jsonify({'error': 'Rendez-vous non trouvé'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/rendezvous/patient/<int:patient_id>', methods=['GET'])
    def get_rendezvous_by_patient(patient_id):
        """Récupérer les rendez-vous d'un patient"""
        try:
            rendezvous = RendezVous.get_by_patient(patient_id)
            rendezvous_data = []
            for r in rendezvous:
                rendezvous_data.append({
                    'id': r.id,
                    'patient_id': r.patient_id,
                    'medecin_id': r.medecin_id,
                    'date_heure': str(r.date_heure) if r.date_heure else None,
                    'statut': r.statut,
                    'notes': r.notes
                })
            return jsonify(rendezvous_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/rendezvous/medecin/<int:medecin_id>', methods=['GET'])
    def get_rendezvous_by_medecin(medecin_id):
        """Récupérer les rendez-vous d'un médecin"""
        try:
            rendezvous = RendezVous.get_by_medecin(medecin_id)
            rendezvous_data = []
            for r in rendezvous:
                rendezvous_data.append({
                    'id': r.id,
                    'patient_id': r.patient_id,
                    'medecin_id': r.medecin_id,
                    'date_heure': str(r.date_heure) if r.date_heure else None,
                    'statut': r.statut,
                    'notes': r.notes
                })
            return jsonify(rendezvous_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/rendezvous', methods=['POST'])
    def create_rendezvous():
        """Créer un nouveau rendez-vous"""
        try:
            data = request.json
            
            # Validation des données
            if not data.get('patient_id') or not data.get('medecin_id') or not data.get('date_heure'):
                return jsonify({'error': 'patient_id, medecin_id et date_heure sont obligatoires'}), 400
            
            rdv = RendezVous(
                patient_id=data['patient_id'],
                medecin_id=data['medecin_id'],
                date_heure=data['date_heure'],
                statut=data.get('statut', 'confirmé'),
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
    
    @app.route('/api/rendezvous/<int:rdv_id>/annuler', methods=['PUT'])
    def annuler_rendezvous(rdv_id):
        """Annuler un rendez-vous"""
        try:
            rdv = RendezVous.get_by_id(rdv_id)
            
            if not rdv:
                return jsonify({'error': 'Rendez-vous non trouvé'}), 404
            
            if rdv.annuler():
                return jsonify({
                    'message': 'Rendez-vous annulé avec succès',
                    'rendezvous': {
                        'id': rdv.id,
                        'statut': rdv.statut
                    }
                })
            else:
                return jsonify({'error': 'Erreur lors de l\'annulation'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500