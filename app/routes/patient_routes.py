# app/routes/patient_routes.py
from flask import Blueprint, request, jsonify, render_template
import jwt
from app.rpc.auth_rpc.auth_rpc import SECRET_KEY
from models.User import User

patient_bp = Blueprint("patient_bp", __name__, url_prefix="/patient")

@patient_bp.route("/dashboard")
def dashboard():
    token = request.cookies.get("access_token")
    if not token:
        return "Utilisateur non connecté", 401

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]
        role = payload["role"]

        # Optionnel : récupérer le nom depuis la DB
        user = User.get_by_id(user_id)
        username = user.nom if user else "Inconnu"

        return render_template("patient/dashboard.html", user_id=user_id, role=role, username=username)
    except jwt.ExpiredSignatureError:
        return "Token expiré", 401
    except Exception as e:
        return str(e), 400
