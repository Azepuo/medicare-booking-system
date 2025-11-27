from flask import jsonify, request
from models.patient import Patient
from models.rendezvous import RendezVous
from models.medecin import Medecin
from models.disponibilite import Disponibilite
from datetime import time

def init_api_routes(app):
    
    # ==================== DISPONIBILITÉS ====================
    
    @app.route('/api/disponibilites', methods=['GET'])
    def get_disponibilites():
        """Récupérer toutes les disponibilités"""
        try:
            # Pour l'instant, on utilise medecin_id=1, à adapter avec l'authentification
            medecin_id = 1
            disponibilites = Disponibilite.get_all(medecin_id)
            
            disponibilites_data = []
            for dispo in disponibilites:
                disponibilites_data.append(dispo.to_dict())
                
            return jsonify({'success': True, 'data': disponibilites_data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/disponibilites/<int:dispo_id>', methods=['GET'])
    def get_disponibilite(dispo_id):
        """Récupérer une disponibilité par ID"""
        try:
            dispo = Disponibilite.get_by_id(dispo_id)
            if dispo:
                return jsonify({
                    'success': True,
                    'data': dispo.to_dict()
                })
            return jsonify({'success': False, 'error': 'Disponibilité non trouvée'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/disponibilites', methods=['POST'])
    def create_disponibilite():
        """Créer une nouvelle disponibilité"""
        try:
            data = request.json
            
            # Validation des données
            if not data.get('jour_semaine') or not data.get('heure_debut') or not data.get('heure_fin'):
                return jsonify({'success': False, 'error': 'Tous les champs sont obligatoires'}), 400
            
            # Validation des heures
            if data['heure_debut'] >= data['heure_fin']:
                return jsonify({'success': False, 'error': 'L\'heure de fin doit être après l\'heure de début'}), 400
            
            # Vérifier les conflits
            medecin_id = 1  # À adapter avec l'authentification
            if Disponibilite.check_conflit(
                medecin_id, 
                data['jour_semaine'], 
                data['heure_debut'], 
                data['heure_fin']
            ):
                return jsonify({'success': False, 'error': 'Conflit avec une disponibilité existante'}), 400
            
            # Créer la disponibilité
            nouvelle_dispo = Disponibilite(
                medecin_id=medecin_id,
                jour_semaine=data['jour_semaine'],
                heure_debut=data['heure_debut'],
                heure_fin=data['heure_fin']
            )
            
            if nouvelle_dispo.save():
                return jsonify({
                    'success': True,
                    'message': 'Disponibilité créée avec succès',
                    'data': nouvelle_dispo.to_dict()
                }), 201
            else:
                return jsonify({'success': False, 'error': 'Erreur lors de la création'}), 500
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/disponibilites/<int:dispo_id>', methods=['PUT'])
    def update_disponibilite(dispo_id):
        """Mettre à jour une disponibilité"""
        try:
            data = request.json
            dispo = Disponibilite.get_by_id(dispo_id)
            
            if not dispo:
                return jsonify({'success': False, 'error': 'Disponibilité non trouvée'}), 404
            
            # Validation des données
            if not data.get('jour_semaine') or not data.get('heure_debut') or not data.get('heure_fin'):
                return jsonify({'success': False, 'error': 'Tous les champs sont obligatoires'}), 400
            
            # Validation des heures
            if data['heure_debut'] >= data['heure_fin']:
                return jsonify({'success': False, 'error': 'L\'heure de fin doit être après l\'heure de début'}), 400
            
            # Vérifier les conflits (exclure l'actuelle)
            medecin_id = 1  # À adapter avec l'authentification
            if Disponibilite.check_conflit(
                medecin_id, 
                data['jour_semaine'], 
                data['heure_debut'], 
                data['heure_fin'],
                exclude_id=dispo_id
            ):
                return jsonify({'success': False, 'error': 'Conflit avec une disponibilité existante'}), 400
            
            # Mettre à jour
            dispo.jour_semaine = data['jour_semaine']
            dispo.heure_debut = data['heure_debut']
            dispo.heure_fin = data['heure_fin']
            
            if dispo.save():
                return jsonify({
                    'success': True,
                    'message': 'Disponibilité mise à jour avec succès',
                    'data': dispo.to_dict()
                })
            else:
                return jsonify({'success': False, 'error': 'Erreur lors de la mise à jour'}), 500
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/disponibilites/<int:dispo_id>', methods=['DELETE'])
    def delete_disponibilite(dispo_id):
        """Supprimer une disponibilité"""
        try:
            dispo = Disponibilite.get_by_id(dispo_id)
            
            if not dispo:
                return jsonify({'success': False, 'error': 'Disponibilité non trouvée'}), 404
            
            if dispo.delete():
                return jsonify({
                    'success': True,
                    'message': 'Disponibilité supprimée avec succès'
                })
            else:
                return jsonify({'success': False, 'error': 'Erreur lors de la suppression'}), 500
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/disponibilites/stats', methods=['GET'])
    def get_disponibilites_stats():
        """Récupérer les statistiques des disponibilités"""
        try:
            medecin_id = 1  # À adapter avec l'authentification
            stats = calculer_statistiques_disponibilites(medecin_id)
            
            return jsonify({
                'success': True,
                'data': stats
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/disponibilites/medecin/<int:medecin_id>', methods=['GET'])
    def get_disponibilites_medecin(medecin_id):
        """Récupérer les disponibilités d'un médecin spécifique"""
        try:
            disponibilites = Disponibilite.get_all(medecin_id)
            
            disponibilites_data = []
            for dispo in disponibilites:
                disponibilites_data.append(dispo.to_dict())
                
            return jsonify({'success': True, 'data': disponibilites_data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # ==================== FONCTIONS UTILITAIRES ====================
    
    def calculer_statistiques_disponibilites(medecin_id):
        """Calculer les statistiques des disponibilités"""
        disponibilites = Disponibilite.get_all(medecin_id)
        
        total_minutes = 0
        jours_travailles = set()
        
        for dispo in disponibilites:
            if isinstance(dispo.heure_debut, str):
                debut = time.fromisoformat(dispo.heure_debut)
                fin = time.fromisoformat(dispo.heure_fin)
            else:
                debut = dispo.heure_debut
                fin = dispo.heure_fin
                
            debut_minutes = debut.hour * 60 + debut.minute
            fin_minutes = fin.hour * 60 + fin.minute
            total_minutes += (fin_minutes - debut_minutes)
            jours_travailles.add(dispo.jour_semaine)
        
        total_heures = total_minutes / 60
        
        return {
            'heures_semaine': round(total_heures, 1),
            'jours_travailles': len(jours_travailles),
            'total_creneaux': len(disponibilites)
        }

    # ==================== PATIENTS ====================
    # [Votre code existant pour patients, médecins, rendez-vous...]
    
    @app.route('/api/patients', methods=['GET'])
    def get_patients():
        """Récupérer tous les patients"""
        try:
            patients = Patient.get_all()
            patients_data = []
            for p in patients:
                patients_data.append(p.to_dict())
            return jsonify(patients_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ... [Le reste de votre code API existant]
    # ==================== PATIENTS ====================
    # [Garder tout le code existant pour patients, médecins, rendez-vous...]
    # ... (votre code existant reste inchangé)

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