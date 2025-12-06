from flask import Blueprint, request, jsonify
from app.auth_rpc.auth_rpc import rpc_login, rpc_register, rpc_register_medecin, rpc_logout

rpc_bp = Blueprint("rpc_bp", __name__, url_prefix="/api/rpc")

@rpc_bp.route("/", methods=["POST"])
def rpc_handler():
    data = request.get_json() or {}
    method = data.get("method")
    params = data.get("params", {})

    if method == "login":
        return jsonify(rpc_login(params))
    elif method == "register":
        return jsonify(rpc_register(params))
    elif method == "register_medecin":
        return jsonify(rpc_register_medecin(params))
    elif method == "logout":
        return jsonify(rpc_logout(params))

    return jsonify({"success": False, "message": "Méthode RPC inconnue"}), 400
