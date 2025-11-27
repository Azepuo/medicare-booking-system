from flask import jsonify, request
from models.patient import Patient
from models.rendezvous import RendezVous
from models.medecin import Medecin
from models.disponibilite import Disponibilite
from datetime import time


def init_api_routes(app):

    # ======================================================
    # ================= DISPONIBILITÉS =====================
    # ======================================================

    @app.route('/api/disponibilites', methods=['GET'])
    def get_disponibilites():
        """Récupérer toutes les disponibilités du médecin connecté"""
        try:
            medecin_id = 1  # TEMP : à remplacer par ID auth
            disponibilites = Disponibilite.get_all(medecin_id)
            return jsonify({
                'success': True,
                'data': [d.to_dict() for d in disponibilites]
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


    @app.route('/api/disponibilites/<int:dispo_id>', methods=['GET'])
    def get_disponibilite(dispo_id):
        """Récupérer une disponibilité par ID"""
        try:
            dispo = Disponibilite.get_by_id(dispo_id)
            if not dispo:
                return jsonify({'success': False, 'error': 'Disponibilité non trouvée'}), 404

            return jsonify({'success': True, 'data': dispo.to_dict()})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


    @app.route('/api/disponibilites', methods=['POST'])
    def create_disponibilite():
        """Créer une nouvelle disponibilité"""
        try:
            data = request.json

            # Validation
            if not data.get('jour_semaine') or not data.get('heure_debut') or not data.get('heure_fin'):
                return jsonify({'success': False, 'error': 'Tous les champs sont obligatoires'}), 400

            if data['heure_debut'] >= data['heure_fin']:
                return jsonify({'success': False, 'error': "L'heure de fin doit être après l'heure de début"}), 400

            medecin_id = 1

            if Disponibilite.check_conflit(medecin_id,
                                           data['jour_semaine'],
                                           data['heure_debut'],
                                           data['heure_fin']):
                return jsonify({'success': False, 'error': 'Conflit avec une disponibilité existante'}), 400

            dispo = Disponibilite(
                medecin_id=medecin_id,
                jour_semaine=data['jour_semaine'],
                heure_debut=data['heure_debut'],
                heure_fin=data['heure_fin']
            )

            if dispo.save():
                return jsonify({
                    'success': True,
                    'message': 'Disponibilité créée avec succès',
                    'data': dispo.to_dict()
                }), 201

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

            if not data.get('jour_semaine') or not data.get('heure_debut') or not data.get('heure_fin'):
                return jsonify({'success': False, 'error': 'Tous les champs sont obligatoires'}), 400

            if data['heure_debut'] >= data['heure_fin']:
                return jsonify({'success': False, 'error': "L'heure de fin doit être après l'heure de début"}), 400

            medecin_id = 1

            if Disponibilite.check_conflit(
                medecin_id,
                data['jour_semaine'],
                data['heure_debut'],
                data['heure_fin'],
                exclude_id=dispo_id
            ):
                return jsonify({'success': False, 'error': 'Conflit avec une disponibilité existante'}), 400

            dispo.jour_semaine = data['jour_semaine']
            dispo.heure_debut = data['heure_debut']
            dispo.heure_fin = data['heure_fin']

            if dispo.save():
                return jsonify({'success': True,
                                'message': 'Disponibilité mise à jour avec succès',
                                'data': dispo.to_dict()})

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
                return jsonify({'success': True, 'message': 'Disponibilité supprimée avec succès'})

            return jsonify({'success': False, 'error': 'Erreur lors de la suppression'}), 500

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


    @app.route('/api/disponibilites/stats', methods=['GET'])
    def get_disponibilites_stats():
        """Statistiques des disponibilités"""
        try:
            medecin_id = 1
            stats = calculer_statistiques_disponibilites(medecin_id)
            return jsonify({'success': True, 'data': stats})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


    @app.route('/api/disponibilites/medecin/<int:medecin_id>', methods=['GET'])
    def get_disponibilites_medecin(medecin_id):
        """Disponibilités d'un médecin"""
        try:
            disponibilites = Disponibilite.get_all(medecin_id)
            return jsonify({'success': True, 'data': [d.to_dict() for d in disponibilites]})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


    # ---------- UTILITAIRE ----------
    def calculer_statistiques_disponibilites(medecin_id):
        disponibilites = Disponibilite.get_all(medecin_id)

        total_minutes = 0
        jours = set()

        for dispo in disponibilites:
            debut = time.fromisoformat(dispo.heure_debut) if isinstance(dispo.heure_debut, str) else dispo.heure_debut
            fin = time.fromisoformat(dispo.heure_fin) if isinstance(dispo.heure_fin, str) else dispo.heure_fin

            total_minutes += (fin.hour * 60 + fin.minute) - (debut.hour * 60 + debut.minute)
            jours.add(dispo.jour_semaine)

        return {
            'heures_semaine': round(total_minutes / 60, 1),
            'jours_travailles': len(jours),
            'total_creneaux': len(disponibilites)
        }

    # ======================================================
    # ======================= PATIENTS =====================
    # ======================================================

    @app.route('/api/patients', methods=['GET'])
    def get_patients():
        try:
            patients = Patient.get_all()
            return jsonify([p.to_dict() for p in patients])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/patients/<int:patient_id>', methods=['GET'])
    def get_patient(patient_id):
        try:
            patient = Patient.get_by_id(patient_id)
            if patient:
                return jsonify(patient.to_dict())
            return jsonify({'error': 'Patient non trouvé'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/patients', methods=['POST'])
    def create_patient():
        try:
            data = request.json

            if not data.get('nom') or not data.get('email'):
                return jsonify({'error': 'Nom et email obligatoires'}), 400

            patient = Patient(
                nom=data['nom'],
                email=data['email'],
                telephone=data.get('telephone', '')
            )

            if patient.save():
                return jsonify({'message': 'Patient créé', 'patient': patient.to_dict()}), 201

            return jsonify({'error': 'Erreur création patient'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/patients/<int:patient_id>', methods=['PUT'])
    def update_patient(patient_id):
        try:
            data = request.json
            patient = Patient.get_by_id(patient_id)

            if not patient:
                return jsonify({'error': 'Patient non trouvé'}), 404

            for field in ['nom', 'email', 'telephone']:
                if field in data:
                    setattr(patient, field, data[field])

            if patient.save():
                return jsonify({'message': 'Patient mis à jour', 'patient': patient.to_dict()})

            return jsonify({'error': 'Erreur mise à jour'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
    def delete_patient(patient_id):
        try:
            patient = Patient.get_by_id(patient_id)
            if not patient:
                return jsonify({'error': 'Patient non trouvé'}), 404

            if patient.delete():
                return jsonify({'message': 'Patient supprimé'})
            return jsonify({'error': 'Erreur suppression'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ======================================================
    # ======================= MÉDECINS =====================
    # ======================================================

    @app.route('/api/medecins', methods=['GET'])
    def get_medecins():
        try:
            medecins = Medecin.get_all()
            return jsonify([m.to_dict() for m in medecins])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/medecins/<int:medecin_id>', methods=['GET'])
    def get_medecin(medecin_id):
        try:
            medecin = Medecin.get_by_id(medecin_id)
            if medecin:
                return jsonify(medecin.to_dict())
            return jsonify({'error': 'Médecin non trouvé'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/medecins/specialite/<string:specialite>', methods=['GET'])
    def get_medecins_by_specialite(specialite):
        try:
            return jsonify([m.to_dict() for m in Medecin.get_by_specialite(specialite)])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ======================================================
    # ===================== RENDEZ-VOUS ====================
    # ======================================================

    @app.route('/api/rendezvous', methods=['GET'])
    def get_rendezvous():
        try:
            rdvs = RendezVous.get_all()
            return jsonify([r.to_dict() for r in rdvs])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/rendezvous/<int:rdv_id>', methods=['GET'])
    def get_rdv(rdv_id):
        try:
            rdv = RendezVous.get_by_id(rdv_id)
            if rdv:
                return jsonify(rdv.to_dict())
            return jsonify({'error': 'RDV non trouvé'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/rendezvous/patient/<int:patient_id>', methods=['GET'])
    def get_rdv_patient(patient_id):
        try:
            return jsonify([r.to_dict() for r in RendezVous.get_by_patient(patient_id)])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/rendezvous/medecin/<int:medecin_id>', methods=['GET'])
    def get_rdv_medecin(medecin_id):
        try:
            return jsonify([r.to_dict() for r in RendezVous.get_by_medecin(medecin_id)])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/rendezvous', methods=['POST'])
    def create_rdv():
        try:
            data = request.json
            rdv = RendezVous(
                patient_id=data['patient_id'],
                medecin_id=data['medecin_id'],
                date_heure=data['date_heure'],
                statut=data.get('statut', 'prévu'),
                notes=data.get('notes', '')
            )

            if rdv.save():
                return jsonify({'message': 'RDV créé', 'rdv': rdv.to_dict()}), 201
            return jsonify({'error': 'Erreur création RDV'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500
