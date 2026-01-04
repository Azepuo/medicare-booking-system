from flask import Blueprint, request, jsonify, make_response
import jwt, datetime, re
import bcrypt
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

    # 🔐 bcrypt (UNIFIÉ)
    user.password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user.save()
    return user

# ---------------- RPC LOGIN ----------------
def rpc_login(params):
    email = params.get("email", "").strip().lower()
    password = params.get("password", "")

    user = get_user_by_email(email)

    if not user or not bcrypt.checkpw(
        password.encode("utf-8"),
        user.password.encode("utf-8")
    ):
        return jsonify({
            "success": False,
            "message": "Email ou mot de passe incorrect"
        }), 401

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
        "PATIENT": "http://127.0.0.1:5001/patient/dashboard",
        "MEDECIN": "http://127.0.0.1:5002/medecin/dashboard",
        "ADMIN":   "http://127.0.0.1:5003/admin/dashboard"
    }

    response = make_response(jsonify({
        "success": True,
        "redirect": redirect_map[user.role]
    }))
    response.set_cookie("access_token", access_token, httponly=True, samesite="Lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Lax")
    return response

import bcrypt
import re
from database.connection import create_connection

EMAIL_REGEX = r"^[^@]+@[^@]+\.[^@]+$"

# ---------------- RPC REGISTER ----------------
def rpc_register(params, role="PATIENT"):
    nom = params.get("fullname", "").strip()
    email = params.get("email", "").strip().lower()
    telephone = params.get("tele", "").strip()
    password = params.get("password", "")
    confirm = params.get("confirm_password", "")

    if not all([nom, email, password, confirm]):
        return {"success": False, "message": "Veuillez remplir tous les champs"}

    if password != confirm:
        return {"success": False, "message": "Les mots de passe ne correspondent pas"}

    if not re.match(EMAIL_REGEX, email):
        return {"success": False, "message": "Email invalide"}

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 🔎 Vérifier email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return {"success": False, "message": "Email déjà utilisé"}

        # 🔐 Hash
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # 1️⃣ INSERT USERS
        cursor.execute("""
            INSERT INTO users (nom, email, telephone, password, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (nom, email, telephone, hashed, role))

        user_id = cursor.lastrowid

        # 2️⃣ INSERT METIER (PATIENT)
        if role == "PATIENT":
            cursor.execute("""
                INSERT INTO patients (user_id, nom, email, telephone, sexe)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, nom, email, telephone, "Non défini"))

        conn.commit()

        return {
            "success": True,
            "message": f"Compte {role.lower()} créé avec succès",
            "user_id": user_id
        }

    except Exception as e:
        conn.rollback()
        print("RPC REGISTER ERROR :", e)
        return {"success": False, "message": "Erreur serveur"}

    finally:
        cursor.close()
        conn.close()


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
            response = make_response(jsonify({
                "success": True,
                "redirect": "/login"
            }))
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response

        return jsonify({"success": False, "message": "Méthode RPC inconnue"}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500
# ---------------- JWT / UTIL ----------------
def get_user_from_token(token=None):
    """
    Récupère les informations de l'utilisateur depuis le JWT.
    Si token non fourni, le prend depuis le cookie 'access_token'.
    Retourne un dictionnaire {'user_id': ..., 'role': ...} ou None si invalide.
    """
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {
            "user_id": payload.get("user_id"),
            "role": payload.get("role")
        }
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_tokens(user: User) -> dict:
    """Génère access_token et refresh_token JWT"""
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

    return {"access_token": access_token, "refresh_token": refresh_token}