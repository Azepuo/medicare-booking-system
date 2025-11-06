# --- routes_dashboard.py ---
from flask import Blueprint, jsonify
from utils.rpc_client import MedecinClient

bp = Blueprint("medecin", __name__, url_prefix="/api/medecin")

# Ton client RPC (vers ton microservice Médecin / RDV)
rpc = MedecinClient("localhost", 8001)  # adapte host/port

@bp.route("/statistiques/summary", methods=["GET"])
def statistiques_summary():
    """
    Résumé pour le tableau de bord du médecin :
    - total_rdv : total des rendez-vous
    - rdv_today : rendez-vous du jour
    - taux_annulation : pourcentage d’annulations
    - last_days : liste d’évolution journalière [{day, count}, ...]
    """
    medecin_id = 1  # à remplacer par session utilisateur authentifiée

    # Exemple d’appel RPC (à adapter à ton service réel)
    stats = rpc.call("get_dashboard_stats", {"medecin_id": medecin_id})

    # Exemple de retour attendu par le frontend :
    # {
    #   "total_rdv": 120,
    #   "rdv_today": 6,
    #   "taux_annulation": 8,
    #   "last_days": [
    #       {"day": "Lun", "count": 4},
    #       {"day": "Mar", "count": 7},
    #       ...
    #   ]
    # }

    return jsonify(stats)
