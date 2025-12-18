# app/routes/authentification/auth_rpc.py
from flask import Blueprint, request, jsonify, make_response
import jwt, datetime, re
from werkzeug.security import generate_password_hash, check_password_hash
from models.User import User

auth_rpc = Blueprint("auth_rpc", __name__)

SECRET_KEY = "secret123"
REFRESH_SECRET_KEY = "refresh123"
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

ROLE_MAP = {
    "patient": "PATIENT",
    "medecin": "MEDECIN",
    "admin": "ADMIN"
}

# ---------------- HELPERS ----------------
def get_user_by_email(email):
    return User.get_by_email(email)

def create_user(nom, email, password, role, telephone=None):
    user = User(nom=nom, email=email, role=role, telephone=telephone)
    # Hash du mot de passe
    user.password = generate_password_hash(password)
    user.save()
    return user

# ---------------- RPC LOGIN ----------------
def rpc_login(params):
    email = params.get("email", "").strip().lower()
    password = params.get("password", "")


    user = get_user_by_email(email)
    if not user or not check_password_hash(user.password, password):
        return jsonify({"success": False, "message": "Email ou mot de passe incorrect"}), 401

    access_token = jwt.encode({
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }, SECRET_KEY, algorithm="HS256")

    refresh_token = jwt.encode({
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, REFRESH_SECRET_KEY, algorithm="HS256")

    redirect_map = {
        "PATIENT": "http://localhost:5003/patient/dashboard",
        "MEDECIN": "http://localhost:5002/medecin/dashboard",
        "ADMIN": "http://localhost:5001/admin/dashboard"
    }

    response = make_response(jsonify({
        "success": True,
        "redirect": redirect_map[user.role]
    }))
    response.set_cookie("access_token", access_token, httponly=True, samesite="Lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Lax")
    return response

# ---------------- RPC REGISTER ----------------
def rpc_register(params, role="PATIENT"):
    nom = params.get("fullname", "").strip()
    email = params.get("email", "").strip().lower()
    telephone = params.get("tele", "").strip()
    password = params.get("password", "")
    confirm = params.get("confirm_password", "")

    if not all([nom, email, password, confirm]):
        return jsonify({"success": False, "message": "Veuillez remplir tous les champs"}), 400

    if password != confirm:
        return jsonify({"success": False, "message": "Les mots de passe ne correspondent pas"}), 400

    if not re.match(EMAIL_REGEX, email):
        return jsonify({"success": False, "message": "Email invalide"}), 400

    if get_user_by_email(email):
        return jsonify({"success": False, "message": "Email déjà utilisé"}), 400

    user = create_user(nom, email, password, role, telephone)
    return jsonify({"success": True, "message": f"Compte {role.lower()} créé avec succès", "user_id": user.id})

# ---------------- HANDLER ----------------
@auth_rpc.route("/api/rpc", methods=["POST"])
def handler():
    data = request.get_json() or {}
    method = data.get("method")
    params = data.get("params", {})

    try:
        if method == "login":
            return rpc_login(params)
        elif method == "register":
            return rpc_register(params, role="PATIENT")
        elif method == "register_medecin":
            return rpc_register(params, role="MEDECIN")
        elif method == "logout":
            response = make_response(jsonify({"success": True, "redirect": "/login"}))
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response
        return jsonify({"success": False, "message": "Méthode RPC inconnue"}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500
