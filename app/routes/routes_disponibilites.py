from flask import Blueprint, request, jsonify
from utils.rpc_client import MedecinClient

bp = Blueprint("medecin_dispo", __name__, url_prefix="/api/medecin/dispo")
rpc = MedecinClient("localhost", 8001)

@bp.route("/", methods=["GET"])
def get_dispos():
    medecin_id = 1
    data = rpc.call("get_disponibilites", {"medecin_id": medecin_id})
    return jsonify(data)

@bp.route("/", methods=["POST"])
def add_dispo():
    body = request.get_json()
    body["medecin_id"] = 1
    result = rpc.call("ajouter_disponibilite", body)
    return jsonify(result)
