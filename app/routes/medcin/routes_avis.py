from flask import Blueprint, jsonify
from utils.rpc_client import MedecinClient

bp = Blueprint("medecin_avis", __name__, url_prefix="/api/medecin/avis")
rpc = MedecinClient("localhost", 8001)

@bp.route("/", methods=["GET"])
def get_avis():
    medecin_id = 1
    data = rpc.call("get_avis_medecin", {"medecin_id": medecin_id})
    return jsonify(data)
