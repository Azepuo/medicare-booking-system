# app/routes/medecin_routes.py
from flask import Blueprint, request, render_template
import jwt
from app.rpc.auth_rpc.auth_rpc import SECRET_KEY
from models.User import User

medecin_bp = Blueprint("medecin_bp", __name__, url_prefix="/medecin")

@medecin_bp.route("/dashboard")
def dashboard():
    token = request.cookies.get("access_token")
    if not token:
        return "Utilisateur non connecté", 401

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]
        role = payload["role"]

        user = User.get_by_id(user_id)
        username = user.nom if user else "Inconnu"
        email = user.email if user else ""

        return render_template(
            "medecin/dashboard.html",
            user_id=user_id,
            role=role,
            username=username,
            email=email
        )

    except jwt.ExpiredSignatureError:
        return "Token expiré", 401
    except Exception as e:
        return str(e), 400
