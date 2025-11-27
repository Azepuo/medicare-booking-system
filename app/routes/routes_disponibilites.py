# app/routes/disponibilites_routes.py
from flask import Blueprint, render_template, jsonify, request
from models.disponibilite import Disponibilite
from datetime import time

disponibilites_bp = Blueprint('disponibilites', __name__)

@disponibilites_bp.route('/disponibilites')
def page_disponibilites():
    """Page principale des disponibilités"""
    # Récupérer les disponibilités du médecin connecté
    medecin_id = 1  # À adapter avec l'authentification
    disponibilites = Disponibilite.get_all(medecin_id)
    
    # Calculer les statistiques
    stats = calculer_statistiques(medecin_id)
    
    return render_template('medecin/disponibilites.html',
                         disponibilites=disponibilites,
                         stats=stats)

@disponibilites_bp.route('/api/disponibilites', methods=['GET'])
def api_get_disponibilites():
    """API: Récupérer toutes les disponibilités"""
    medecin_id = 1  # À adapter
    disponibilites = Disponibilite.get_all(medecin_id)
    
    return jsonify({
        'success': True,
        'data': [dispo.to_dict() for dispo in disponibilites]
    })

@disponibilites_bp.route('/api/disponibilites', methods=['POST'])
def api_add_disponibilite():
    """API: Ajouter une nouvelle disponibilité"""
    try:
        data = request.get_json()
        
        # Validation des données
        if not all(k in data for k in ['jour_semaine', 'heure_debut', 'heure_fin']):
            return jsonify({'success': False, 'error': 'Données manquantes'}), 400
        
        # Validation des heures
        if data['heure_debut'] >= data['heure_fin']:
            return jsonify({'success': False, 'error': 'L\'heure de fin doit être après l\'heure de début'}), 400
        
        # Vérifier les conflits
        medecin_id = 1
        if Disponibilite.check_conflit(medecin_id, data['jour_semaine'], data['heure_debut'], data['heure_fin']):
            return jsonify({'success': False, 'error': 'Conflit avec une disponibilité existante'}), 400
        
        # Créer la nouvelle disponibilité
        nouvelle_dispo = Disponibilite(
            medecin_id=medecin_id,
            jour_semaine=data['jour_semaine'],
            heure_debut=data['heure_debut'],
            heure_fin=data['heure_fin']
        )
        
        if nouvelle_dispo.save():
            return jsonify({
                'success': True,
                'message': 'Disponibilité ajoutée avec succès',
                'data': nouvelle_dispo.to_dict()
            })
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de la sauvegarde'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@disponibilites_bp.route('/api/disponibilites/<int:id>', methods=['PUT'])
def api_update_disponibilite(id):
    """API: Modifier une disponibilité"""
    try:
        data = request.get_json()
        disponibilite = Disponibilite.get_by_id(id)
        
        if not disponibilite:
            return jsonify({'success': False, 'error': 'Disponibilité non trouvée'}), 404
        
        # Vérifier les conflits (exclure l'actuelle)
        medecin_id = 1
        if Disponibilite.check_conflit(medecin_id, data['jour_semaine'], data['heure_debut'], data['heure_fin'], exclude_id=id):
            return jsonify({'success': False, 'error': 'Conflit avec une disponibilité existante'}), 400
        
        # Mettre à jour
        disponibilite.jour_semaine = data['jour_semaine']
        disponibilite.heure_debut = data['heure_debut']
        disponibilite.heure_fin = data['heure_fin']
        
        if disponibilite.save():
            return jsonify({
                'success': True,
                'message': 'Disponibilité modifiée avec succès',
                'data': disponibilite.to_dict()
            })
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de la mise à jour'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@disponibilites_bp.route('/api/disponibilites/<int:id>', methods=['DELETE'])
def api_delete_disponibilite(id):
    """API: Supprimer une disponibilité"""
    try:
        disponibilite = Disponibilite.get_by_id(id)
        
        if not disponibilite:
            return jsonify({'success': False, 'error': 'Disponibilité non trouvée'}), 404
        
        if disponibilite.delete():
            return jsonify({
                'success': True,
                'message': 'Disponibilité supprimée avec succès'
            })
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de la suppression'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@disponibilites_bp.route('/api/disponibilites/stats')
def api_get_stats():
    """API: Récupérer les statistiques"""
    medecin_id = 1  # À adapter
    stats = calculer_statistiques(medecin_id)
    
    return jsonify({
        'success': True,
        'data': stats
    })

def calculer_statistiques(medecin_id):
    """Calculer les statistiques hebdomadaires"""
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