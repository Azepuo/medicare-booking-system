from flask import Flask, render_template, jsonify, request
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.patient import Patient
from models.medecin import Medecin
from models.rendezvous import RendezVous

app = Flask(__name__)

# ==================== ROUTES API ====================

# PATIENTS
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
                'telephone': patient.telephone
            })
        return jsonify({'error': 'Patient non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients', methods=['POST'])
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
                'id': patient.id
            }), 201
        else:
            return jsonify({'error': 'Erreur lors de la création'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# MÉDECINS
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

# RENDEZ-VOUS
@app.route('/api/rendezvous', methods=['GET'])
def get_rendezvous():
    """Récupérer tous les rendez-vous"""
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

@app.route('/api/rendezvous', methods=['POST'])
def create_rendezvous():
    """Créer un nouveau rendez-vous"""
    try:
        data = request.json
        
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
                'id': rdv.id
            }), 201
        else:
            return jsonify({'error': 'Erreur lors de la création'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROUTES TEMPLATES ====================

@app.route('/')
def accueil():
    return "🏥 Bienvenue sur Medicare Booking - API est active!"

@app.route('/test')
def test():
    return jsonify({
        'message': 'API fonctionne!',
        'endpoints': {
            'patients': '/api/patients',
            'medecins': '/api/medecins', 
            'rendezvous': '/api/rendezvous'
        }
    })

if __name__ == '__main__':
    print("🚀 Serveur Flask démarré sur http://localhost:5000")
    print("📋 Endpoints disponibles:")
    print("   GET  /api/patients")
    print("   POST /api/patients") 
    print("   GET  /api/medecins")
    print("   GET  /api/rendezvous")
    print("   POST /api/rendezvous")
    print("   GET  /test")
    app.run(debug=True, host='0.0.0.0', port=5000)