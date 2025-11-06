from flask import Blueprint, request, jsonify
from utils.rpc_client import MedecinClient

bp = Blueprint("medecin_chat", __name__, url_prefix="/api/medecin/chat")
rpc = MedecinClient("localhost", 8001)

@bp.route("/conversations", methods=["GET"])
def get_conversations():
    """Liste des patients avec lesquels le médecin a déjà échangé"""
    medecin_id = 1
    data = rpc.call("get_chat_conversations", {"medecin_id": medecin_id})
    return jsonify(data)

@bp.route("/messages/<int:patient_id>", methods=["GET"])
def get_messages(patient_id):
    """Récupère les messages d'une conversation médecin ↔ patient"""
    medecin_id = 1
    data = rpc.call("get_chat_messages", {"medecin_id": medecin_id, "patient_id": patient_id})
    return jsonify(data)

@bp.route("/messages", methods=["POST"])
def send_message():
    """Envoie un message au patient"""
    body = request.get_json()
    body["medecin_id"] = 1
    result = rpc.call("send_chat_message", body)
    return jsonify(result)
