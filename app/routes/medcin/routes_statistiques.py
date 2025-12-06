from flask import Blueprint, jsonify
from utils.rpc_client import MedecinClient

bp = Blueprint("medecin_stats", __name__, url_prefix="/api/medecin/statistiques")
rpc = MedecinClient("localhost", 8001)

@bp.route("/details", methods=["GET"])
def statistiques_details():
    medecin_id = 1
    data = rpc.call("get_statistiques_completes", {"medecin_id": medecin_id})
    # Exemple : {"labels":["Jan","Fév"], "values":[40,52]}
    return jsonify(data)
