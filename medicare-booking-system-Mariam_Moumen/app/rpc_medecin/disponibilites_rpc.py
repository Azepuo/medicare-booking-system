# app/rpc_medecin/disponibilites_rpc.py
from flask import Blueprint, request, jsonify
from .disponibilites_rpc_methods import list_dispo, get_dispo, create_dispo, update_dispo, delete_dispo
from app.rpc.auth_rpc.auth_rpc import get_user_from_token

disponibilites_rpc = Blueprint("disponibilites_rpc", __name__, url_prefix="/medecin/rpc/disponibilites")

def get_medecin_id_from_user_id(user_id):
    """
    Récupère le vrai medecin_id à partir du user_id
    en interrogeant la table medecins.
    
    Retourne:
        - int: medecin_id si trouvé
        - None: si non trouvé
    """
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id FROM medecins WHERE user_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        return result['id'] if result else None
    except Exception as e:
        print(f"Erreur lors de la récupération du medecin_id: {e}")
        return None

# ----------------- LIST -----------------
@disponibilites_rpc.route("/list", methods=["GET"])
def list_all_dispos():
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({"ok": False, "error": "Utilisateur non authentifié"}), 401
        
        # Récupérer le vrai medecin_id
        medecin_id = get_medecin_id_from_user_id(user["user_id"])
        if medecin_id is None:
            return jsonify({"ok": False, "error": "Médecin non trouvé"}), 404
        
        # Vérifier si on veut seulement aujourd'hui
        today_only = request.args.get('today') == '1'
        
        dispos = list_dispo(medecin_id, today_only)
        return jsonify({
            "ok": True, 
            "data": dispos,
            "count": len(dispos)
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ----------------- GET -----------------
@disponibilites_rpc.route("/get/<int:dispo_id>", methods=["GET"])
def get_single_dispo(dispo_id):
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({"ok": False, "error": "Utilisateur non authentifié"}), 401
        
        # Récupérer le vrai medecin_id
        medecin_id = get_medecin_id_from_user_id(user["user_id"])
        if medecin_id is None:
            return jsonify({"ok": False, "error": "Médecin non trouvé"}), 404

        dispo = get_dispo(dispo_id)
        # Vérifier que la disponibilité appartient à ce médecin
        if dispo and dispo['medecin_id'] == medecin_id:
            return jsonify({"ok": True, "data": dispo})
        return jsonify({"ok": False, "error": "Disponibilité non trouvée ou accès non autorisé"}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ----------------- CREATE -----------------
@disponibilites_rpc.route("/create", methods=["POST"])
def create_new_dispo():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400
    
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({"ok": False, "error": "Utilisateur non authentifié"}), 401
        
        # Récupérer le vrai medecin_id
        medecin_id = get_medecin_id_from_user_id(user["user_id"])
        if medecin_id is None:
            return jsonify({"ok": False, "error": "Médecin non trouvé"}), 404

        # Validation des champs obligatoires
        required_fields = ['jour_semaine', 'heure_debut', 'heure_fin']
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return jsonify({"ok": False, "error": f"Champs requis manquants: {', '.join(missing)}"}), 400
        
        # Vérifier que l'heure de début est avant l'heure de fin
        if data['heure_debut'] >= data['heure_fin']:
            return jsonify({"ok": False, "error": "L'heure de début doit être avant l'heure de fin"}), 400

        payload = {
            'medecin_id': medecin_id,  # Utiliser le vrai medecin_id
            'jour_semaine': data.get('jour_semaine'),
            'heure_debut': data.get('heure_debut'),
            'heure_fin': data.get('heure_fin')
        }
        
        new_dispo = create_dispo(payload)
        return jsonify({
            "ok": True, 
            "data": new_dispo,
            "message": "Disponibilité créée avec succès"
        })
        
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"Erreur serveur: {str(e)}"}), 500

# ----------------- UPDATE -----------------
@disponibilites_rpc.route("/update/<int:dispo_id>", methods=["POST", "PUT"])
def update_existing_dispo(dispo_id):
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Données JSON requises"}), 400
    
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({"ok": False, "error": "Utilisateur non authentifié"}), 401
        
        # Récupérer le vrai medecin_id
        medecin_id = get_medecin_id_from_user_id(user["user_id"])
        if medecin_id is None:
            return jsonify({"ok": False, "error": "Médecin non trouvé"}), 404

        # Vérifier que la disponibilité existe et appartient à l'utilisateur
        dispo = get_dispo(dispo_id)
        if not dispo or dispo['medecin_id'] != medecin_id:
            return jsonify({"ok": False, "error": "Disponibilité non trouvée ou accès non autorisé"}), 404
        
        # Vérifier les heures si fournies
        if 'heure_debut' in data and 'heure_fin' in data:
            if data['heure_debut'] >= data['heure_fin']:
                return jsonify({"ok": False, "error": "L'heure de début doit être avant l'heure de fin"}), 400
        
        payload = {k: data[k] for k in ['jour_semaine', 'heure_debut', 'heure_fin'] if k in data}
        
        updated_dispo = update_dispo(dispo_id, payload)
        return jsonify({
            "ok": True, 
            "data": updated_dispo,
            "message": "Disponibilité mise à jour avec succès"
        })
        
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"Erreur serveur: {str(e)}"}), 500

# ----------------- DELETE -----------------
@disponibilites_rpc.route("/delete/<int:dispo_id>", methods=["DELETE"])
def delete_existing_dispo(dispo_id):
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({"ok": False, "error": "Utilisateur non authentifié"}), 401
        
        # Récupérer le vrai medecin_id
        medecin_id = get_medecin_id_from_user_id(user["user_id"])
        if medecin_id is None:
            return jsonify({"ok": False, "error": "Médecin non trouvé"}), 404

        # Vérifier que la disponibilité existe et appartient à l'utilisateur
        dispo = get_dispo(dispo_id)
        if not dispo or dispo['medecin_id'] != medecin_id:
            return jsonify({"ok": False, "error": "Disponibilité non trouvée ou accès non autorisé"}), 404

        success = delete_dispo(dispo_id)
        if success:
            return jsonify({
                "ok": True, 
                "message": "Disponibilité supprimée avec succès"
            })
        else:
            return jsonify({"ok": False, "error": "Erreur lors de la suppression"}), 500
            
    except Exception as e:
        return jsonify({"ok": False, "error": f"Erreur serveur: {str(e)}"}), 500