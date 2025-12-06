from flask import Blueprint, request, jsonify
from utils.rpc_client import MedecinClient

bp = Blueprint("medecin_profil", __name__, url_prefix="/api/medecin/profil")
rpc = MedecinClient("localhost", 8001)

@bp.route("/", methods=["GET"])
def get_profil():
    medecin_id = 1
    data = rpc.call("get_medecin_profil", {"medecin_id": medecin_id})
    return jsonify(data)

@bp.route("/", methods=["POST"])
def update_profil():
    body = request.get_json()
    body["medecin_id"] = 1
    result = rpc.call("update_medecin_profil", body)
    return jsonify(result)
