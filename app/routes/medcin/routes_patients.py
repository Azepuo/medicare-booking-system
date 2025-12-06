from flask import Blueprint, jsonify
from utils.rpc_client import MedecinClient

bp = Blueprint("medecin_patients", __name__, url_prefix="/api/medecin/patients")
rpc = MedecinClient("localhost", 8001)

@bp.route("/", methods=["GET"])
def get_patients():
    medecin_id = 1
    data = rpc.call("get_patients_by_medecin", {"medecin_id": medecin_id})
    return jsonify(data)
