# app/rpc/auth_rpc/auth_rpc.py
from flask import Blueprint, request, jsonify, make_response
import jwt
import datetime
import re
from werkzeug.security import generate_password_hash, check_password_hash
from models.User import User

auth_rpc = Blueprint("auth_rpc", __name__)

# ---------------- CONSTANTES ----------------
SECRET_KEY = "secret123"
REFRESH_SECRET_KEY = "refresh123"
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

ROLE_MAP = {
    "patient": "PATIENT",
    "medecin": "MEDECIN",
    "admin": "ADMIN"
}

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

def redirect_url_for_role(role: str) -> str:
    """Retourne l'URL de redirection selon le rôle"""
    return {
        "PATIENT": "http://localhost:5001/patient/dashboard",
        "MEDECIN": "http://127.0.0.1:5002/medecin/dashboard",
        "ADMIN": "http://localhost:5003/admin/dashboard"
    }.get(role, "/login")

# ---------------- HELPERS ----------------
def get_user_by_email(email: str) -> User | None:
    """Retourne l'objet User si trouvé, sinon None"""
    return User.get_by_email(email)

def create_user(nom: str, email: str, password: str, role: str, telephone: str | None = None) -> User:
    """Crée et sauvegarde un nouvel utilisateur avec mot de passe hashé"""
    user = User(nom=nom, email=email, role=role, telephone=telephone)
    user.password = generate_password_hash(password)
    user.save()
    return user

# ---------------- RPC LOGIN ----------------
# app/routes/authentification/auth_rpc.py
def rpc_login(params: dict):
    email = params.get("email", "").strip().lower()
    password = params.get("password", "")

    user = get_user_by_email(email)
    if not user or not check_password_hash(user.password, password):
        return jsonify({"success": False, "message": "Email ou mot de passe incorrect"}), 401

    # ✅ CRÉATION AUTOMATIQUE DU PROFIL MÉDECIN SI NÉCESSAIRE
    if user.role == "MEDECIN":
        from models.medecin import Medecin  # Import local pour éviter les imports circulaires
        medecin = Medecin.get_by_user_id(user.id)
        if not medecin:
            print(f"🔄 Création automatique du profil médecin pour user_id: {user.id}")
            medecin = Medecin.create_from_user(
                user_id=user.id,
                nom=user.nom,
                email=user.email,
                telephone=user.telephone or ""
            )
            if medecin:
                print(f"✅ Profil médecin créé avec succès, ID: {medecin.id}")
            else:
                print(f"❌ Échec création profil médecin pour user_id: {user.id}")

    tokens = generate_tokens(user)
    response = make_response(jsonify({
        "success": True,
        "redirect": redirect_url_for_role(user.role),
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "role": user.role,
        "user_id": user.id,
        "user_name": user.nom,
        "message": "Connexion réussie"
    }))
    response.set_cookie("access_token", tokens["access_token"], httponly=True, samesite="Lax")
    response.set_cookie("refresh_token", tokens["refresh_token"], httponly=True, samesite="Lax")
    return response

# ---------------- RPC REGISTER ----------------
def rpc_register(params: dict, role="PATIENT"):
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

# ---------------- HANDLER RPC ----------------
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
