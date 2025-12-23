"""
Serveur XML-RPC pour le système de réservation médicale
"""
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import threading
from datetime import datetime, timedelta

# Données de test
admin_data = {
    "id": 1,
    "nom_complet": "Administrateur Système",
    "email": "admin@medecin.com",
    "telephone": "+33612345678",
    "username": "admin",
    "photo": None
}

stats_data = {
    "total_patients": 45,
    "total_medecins": 12,
    "total_rdv": 128,
    "total_factures": 85
}

tasks_data = [
    {"id": 1, "titre": "Vérifier les paiements", "statut": "en_cours"},
    {"id": 2, "titre": "Envoyer rappels RDV", "statut": "complétée"},
    {"id": 3, "titre": "Générer rapports", "statut": "en_attente"}
]

rdv_data = [
    {
        "id": 1,
        "patient_nom": "Dupont Jean",
        "medecin": "Dr. Martin",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "raison": "Consultation générale"
    },
    {
        "id": 2,
        "patient_nom": "Durand Marie",
        "medecin": "Dr. Bernard",
        "date": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
        "raison": "Suivi post-opératoire"
    }
]

class AdminRPCMethods:
    """Méthodes RPC pour l'administration"""
    
    @staticmethod
    def get_admin():
        """Retourne les infos de l'admin"""
        return admin_data
    
    @staticmethod
    def update_admin(data):
        """Met à jour les infos admin"""
        global admin_data
        admin_data.update(data)
        return {"success": True}
    
    @staticmethod
    def update_admin_password(current_pwd, new_pwd):
        """Met à jour le mot de passe admin"""
        # Pour le développement, on accepte tout
        return {"success": True}
    
    @staticmethod
    def get_stats():
        """Retourne les statistiques"""
        return stats_data
    
    @staticmethod
    def liste_taches():
        """Retourne la liste des tâches"""
        return tasks_data
    
    @staticmethod
    def liste_rdv_aujourdhui():
        """Retourne les RDV d'aujourd'hui"""
        return rdv_data
    
    @staticmethod
    def get_medecins():
        """Retourne la liste des médecins"""
        return [
            {"id": 1, "nom": "Dr. Martin", "specialite": "Généraliste"},
            {"id": 2, "nom": "Dr. Bernard", "specialite": "Cardiologue"},
            {"id": 3, "nom": "Dr. Dupont", "specialite": "Dermatologue"}
        ]
    
    @staticmethod
    def get_patients():
        """Retourne la liste des patients"""
        return [
            {"id": 1, "nom": "Dupont Jean", "email": "jean@example.com"},
            {"id": 2, "nom": "Durand Marie", "email": "marie@example.com"},
            {"id": 3, "nom": "Moreau Pierre", "email": "pierre@example.com"}
        ]
    
    @staticmethod
    def add_medecin(data):
        """Ajoute un médecin"""
        return {"success": True, "id": 4}
    
    @staticmethod
    def update_medecin(medecin_id, data):
        """Mise à jour d'un médecin"""
        return {"success": True}
    
    @staticmethod
    def delete_medecin(medecin_id):
        """Supprime un médecin"""
        return {"success": True}
    
    @staticmethod
    def add_patient(data):
        """Ajoute un patient"""
        return {"success": True, "id": 4}
    
    @staticmethod
    def update_patient(patient_id, data):
        """Mise à jour d'un patient"""
        return {"success": True}
    
    @staticmethod
    def delete_patient(patient_id):
        """Supprime un patient"""
        return {"success": True}
    
    @staticmethod
    def get_rdv():
        """Retourne tous les RDV"""
        return rdv_data
    
    @staticmethod
    def add_rdv(data):
        """Ajoute un RDV"""
        return {"success": True, "id": 3}
    
    @staticmethod
    def update_rdv(rdv_id, data):
        """Mise à jour d'un RDV"""
        return {"success": True}
    
    @staticmethod
    def delete_rdv(rdv_id):
        """Supprime un RDV"""
        return {"success": True}
    
    @staticmethod
    def get_factures():
        """Retourne la liste des factures"""
        return [
            {"id": 1, "patient": "Dupont Jean", "montant": 50.00, "date": "2025-11-01"},
            {"id": 2, "patient": "Durand Marie", "montant": 75.00, "date": "2025-11-05"}
        ]
    
    @staticmethod
    def add_facture(data):
        """Ajoute une facture"""
        return {"success": True, "id": 3}
    
    @staticmethod
    def update_facture(facture_id, data):
        """Mise à jour d'une facture"""
        return {"success": True}
    
    @staticmethod
    def delete_facture(facture_id):
        """Supprime une facture"""
        return {"success": True}


def run_server(port=8002):
    """Démarre le serveur RPC"""
    server = SimpleXMLRPCServer(
        ("localhost", port),
        requestHandler=SimpleXMLRPCRequestHandler,
        allow_none=True
    )
    
    # Enregistrer les méthodes
    methods = AdminRPCMethods()
    for method_name in dir(methods):
        if not method_name.startswith('_'):
            method = getattr(methods, method_name)
            if callable(method):
                server.register_function(method, method_name)
    
    print(f"✅ Serveur RPC démarré sur http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
# app/rdv/api.py
from flask import Blueprint, jsonify, request
from datetime import date
from app.rpc_medecin import rdv as rdv_module  # ⬅️ Renommez l'import

bp = Blueprint('rdv_api', __name__, url_prefix='/rpc/rdv')

@bp.route('/list_today', methods=['GET'])
def list_today():
    d = request.args.get('date')
    try:
        the_date = date.fromisoformat(d) if d else date.today()
    except Exception:
        return jsonify({'ok': False, 'error': 'Format date invalide (YYYY-MM-DD attendu)'}), 400
    try:
        data = rdv_module.list_rdv_for_date(the_date)  # ⬅️ Utilisez le nouveau nom
        return jsonify({'ok': True, 'data': data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/get/<int:rdv_id>', methods=['GET'])
def api_get(rdv_id):
    try:
        r = rdv_module.get_rdv(rdv_id)  # ⬅️ Utilisez le nouveau nom
        return jsonify({'ok': True, 'data': r})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/create', methods=['POST'])
def api_create():
    payload = request.get_json(force=True)
    try:
        new_rdv = rdv_module.create_rdv(payload)  # ⬅️ Utilisez le nouveau nom
        return jsonify({'ok': True, 'data': new_rdv}), 201
    except ValueError as e:
        return jsonify({'ok': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/update/<int:rdv_id>', methods=['PUT','PATCH'])
def api_update(rdv_id):
    payload = request.get_json(force=True)
    try:
        r = rdv_module.update_rdv(rdv_id, payload)  # ⬅️ Utilisez le nouveau nom
        if r is None:
            return jsonify({'ok': False, 'error': 'Not found'}), 404
        return jsonify({'ok': True, 'data': r})
    except ValueError as e:
        return jsonify({'ok': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/delete/<int:rdv_id>', methods=['DELETE'])
def api_delete(rdv_id):
    try:
        ok = rdv_module.delete_rdv(rdv_id)  # ⬅️ Utilisez le nouveau nom
        if not ok:
            return jsonify({'ok': False, 'error': 'Not found'}), 404
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/patients', methods=['GET'])
def api_patients():
    try:
        data = rdv_module.list_patients()  # ⬅️ Utilisez le nouveau nom
        return jsonify({'ok': True, 'data': data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route('/medecins', methods=['GET'])
def api_medecins():
    try:
        data = rdv_module.list_medecins()  # ⬅️ Utilisez le nouveau nom
        return jsonify({'ok': True, 'data': data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    
