from flask import Blueprint, request, jsonify
from flask_login import current_user
from .api import rpc_login, rpc_register, rpc_logout
from app.extensions import socketio

rpc_bp = Blueprint("rpc_bp", __name__)

@rpc_bp.route("/", methods=["POST"])
def rpc_handler():
    data = request.get_json() or {}
    method = data.get("method")
    params = data.get("params", {})

    if method == "login":
        return rpc_login(params)
    elif method == "register":
        return rpc_register(params)
    elif method == "logout":
        return rpc_logout(params)

    return jsonify({"success": False, "message": "Méthode RPC inconnue"}), 400

@socketio.on("connect")
def handle_connect():
    if current_user.is_authenticated:
        socketio.join_room(f"user_{current_user.id}")
