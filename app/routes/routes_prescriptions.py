from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for

bp = Blueprint('prescriptions', __name__)

# Données simulées (à remplacer par votre base de données)
prescriptions_data = [
    {
        'id': 1,
        'patient_nom': 'Marie Dupont',
        'patient_age': 45,
        'date_prescription': '2024-01-15',
        'medicaments': [
            {'nom': 'Paracétamol', 'posologie': '1 comprimé 3 fois par jour', 'duree': '7 jours'},
            {'nom': 'Ibuprofène', 'posologie': '1 comprimé 2 fois par jour', 'duree': '5 jours'}
        ],
        'instructions': 'Prendre après les repas. Éviter l\'alcool.',
        'statut': 'active'
    },
    {
        'id': 2,
        'patient_nom': 'Pierre Martin',
        'patient_age': 52,
        'date_prescription': '2024-01-14',
        'medicaments': [
            {'nom': 'Amoxicilline', 'posologie': '1 gélule 3 fois par jour', 'duree': '10 jours'}
        ],
        'instructions': 'Prendre à jeun. Compléter le traitement.',
        'statut': 'active'
    }
]

@bp.route('/prescriptions')
def liste_prescriptions():
    return render_template('medecin/prescriptions.html', prescriptions=prescriptions_data)

@bp.route('/prescriptions/ajouter', methods=['GET', 'POST'])
def ajouter_prescription():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nouvelle_prescription = {
            'id': len(prescriptions_data) + 1,
            'patient_nom': request.form.get('patient_nom'),
            'patient_age': request.form.get('patient_age'),
            'date_prescription': request.form.get('date_prescription'),
            'medicaments': [],
            'instructions': request.form.get('instructions'),
            'statut': 'active'
        }
        
        # Ajouter les médicaments
        medicaments_noms = request.form.getlist('medicament_nom[]')
        medicaments_posologies = request.form.getlist('medicament_posologie[]')
        medicaments_durees = request.form.getlist('medicament_duree[]')
        
        for i in range(len(medicaments_noms)):
            if medicaments_noms[i].strip():
                nouvelle_prescription['medicaments'].append({
                    'nom': medicaments_noms[i],
                    'posologie': medicaments_posologies[i],
                    'duree': medicaments_durees[i]
                })
        
        prescriptions_data.append(nouvelle_prescription)
        return jsonify({'success': True, 'message': 'Prescription ajoutée avec succès'})
    
    return render_template('medecin/ajouter_prescription.html')

@bp.route('/prescriptions/modifier/<int:prescription_id>', methods=['GET', 'POST'])
def modifier_prescription(prescription_id):
    prescription = next((p for p in prescriptions_data if p['id'] == prescription_id), None)
    
    if not prescription:
        return jsonify({'success': False, 'message': 'Prescription non trouvée'}), 404
    
    if request.method == 'POST':
        # Mettre à jour la prescription
        prescription['patient_nom'] = request.form.get('patient_nom')
        prescription['patient_age'] = request.form.get('patient_age')
        prescription['date_prescription'] = request.form.get('date_prescription')
        prescription['instructions'] = request.form.get('instructions')
        
        # Mettre à jour les médicaments
        prescription['medicaments'] = []
        medicaments_noms = request.form.getlist('medicament_nom[]')
        medicaments_posologies = request.form.getlist('medicament_posologie[]')
        medicaments_durees = request.form.getlist('medicament_duree[]')
        
        for i in range(len(medicaments_noms)):
            if medicaments_noms[i].strip():
                prescription['medicaments'].append({
                    'nom': medicaments_noms[i],
                    'posologie': medicaments_posologies[i],
                    'duree': medicaments_durees[i]
                })
        
        return jsonify({'success': True, 'message': 'Prescription modifiée avec succès'})
    
    return render_template('medecin/modifier_prescription.html', prescription=prescription)

@bp.route('/prescriptions/supprimer/<int:prescription_id>', methods=['POST'])
def supprimer_prescription(prescription_id):
    global prescriptions_data
    prescriptions_data = [p for p in prescriptions_data if p['id'] != prescription_id]
    return jsonify({'success': True, 'message': 'Prescription supprimée avec succès'})

@bp.route('/prescriptions/archiver/<int:prescription_id>', methods=['POST'])
def archiver_prescription(prescription_id):
    prescription = next((p for p in prescriptions_data if p['id'] == prescription_id), None)
    if prescription:
        prescription['statut'] = 'archived'
        return jsonify({'success': True, 'message': 'Prescription archivée'})
    return jsonify({'success': False, 'message': 'Prescription non trouvée'}), 404