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
