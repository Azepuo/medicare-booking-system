from flask import Blueprint, request, jsonify
import jwt
from models.User import User

admin_bp = Blueprint("admin_bp", __name__)

SECRET_KEY = "secret123"

@admin_bp.route("/dashboard")
def dashboard():
    access_token = request.cookies.get("access_token")
    if not access_token:
        return "Token manquant", 401

    try:
        data = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
        user_id = data["user_id"]
        role = data["role"]
        return jsonify({"message": "Dashboard Admin", "user_id": user_id, "role": role})
    except jwt.ExpiredSignatureError:
        return "Token expiré", 401
    except Exception as e:
        return str(e), 400
