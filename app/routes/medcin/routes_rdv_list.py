from flask import Blueprint, jsonify
from utils.rpc_client import MedecinClient

bp = Blueprint("medecin_rdv", __name__, url_prefix="/api/medecin/rdv")
rpc = MedecinClient("localhost", 8001)

@bp.route("/today", methods=["GET"])
def rdv_today():
    """Retourne les rendez-vous du jour pour un médecin donné."""
    medecin_id = 1  # à remplacer par la session réelle
    data = rpc.call("get_rdv_today", {"medecin_id": medecin_id})
    # Format attendu :
    # [
    #   {"heure": "09:00", "patient": "Fatima Z.", "motif": "Consultation", "statut": "Confirmé"},
    #   ...
    # ]
    return jsonify(data)
