from flask import Blueprint, jsonify
from utils.rpc_client import MedecinClient

bp = Blueprint("medecin_agenda", __name__, url_prefix="/api/medecin/agenda")
rpc = MedecinClient("localhost", 8001)

@bp.route("/week", methods=["GET"])
def agenda_week():
    """Renvoie l’agenda complet de la semaine."""
    medecin_id = 1
    data = rpc.call("get_agenda_week", {"medecin_id": medecin_id})
    # Exemple de retour :
    # {"Lundi": [{"heure": "09:00", "patient": "Ali B.", "motif": "Suivi"}], "Mardi": [...], ...}
    return jsonify(data)
