from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user
from app.extensions import socketio
from models.patient import Patient
from models.medecin import Medecin
from models.admin import Admin
import re

EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

auth = Blueprint("auth", __name__, template_folder="templates/auth")

# ------------------ PAGES ------------------
@auth.route("/login", methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        role = current_user.get_id().split(":")[0]
        return redirect(url_for(f"{role}.dashboard"))
    return render_template("auth/login.html")



@auth.route("/register", methods=["GET"])
def register_page():
    if current_user.is_authenticated:
        role = current_user.get_id().split(":")[0]
        return redirect(url_for(f"{role}.dashboard"))
    return render_template("auth/register.html")



@auth.route("/logout")
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("auth.login_page"))


# ------------------- Helpers -------------------
ROLE_MAP = {
    "patient": Patient,
    "medecin": Medecin,
    "admin": Admin
}

def get_user(role: str, email: str):
    """Retourne l’utilisateur d’un rôle donné et un email donné"""
    cls = ROLE_MAP.get(role)
    return cls.get_by_email(email) if cls else None

def create_user(role: str, nom: str, email: str, tele: str, password: str):
    """Crée un utilisateur selon le rôle et retourne l’objet"""
    cls = ROLE_MAP.get(role)
    if not cls:
        return None

    if role == "medecin":
        user = cls(nom=nom, email=email, telephone=tele, approved=False)
    else:
        user = cls(nom=nom, email=email, telephone=tele)

    user.set_password(password)
    return user if user.save() else None


# ------------------- RPC -------------------
def rpc_login(params):
    email = params.get("email", "").lower().strip()
    password = params.get("password", "")
    role = params.get("role", "patient").lower()

    user = get_user(role, email)
    
    if role == "medecin" and user and getattr(user, "approved", False) is False:
        return {"success": False, "message": "Compte médecin en attente d'approbation"}

    
    if not user or not user.check_password(password):
        
        return {"success": False, "message": "Email ou mot de passe incorrect"}

    login_user(user)
    redirect_map = {r: f"/{r}/dashboard" for r in ROLE_MAP.keys()}
    return {"success": True, "redirect": redirect_map.get(role, "/")}


def rpc_register(params, role="patient"):
    nom = params.get("fullname", "").strip()
    email = params.get("email", "").strip().lower()
    tele = params.get("tele", "").strip()
    password = params.get("password", "")
    confirm = params.get("confirm_password", "")

    if not all([nom, email, tele, password, confirm]):
        return {"success": False, "message": "Veuillez remplir tous les champs"}

    if password != confirm:
        return {"success": False, "message": "Les mots de passe ne correspondent pas"}

    if not re.match(EMAIL_REGEX, email):
        return {"success": False, "message": "Email invalide"}

    if any(get_user(r, email) for r in ROLE_MAP.keys()):
        return {"success": False, "message": "Email déjà utilisé"}

    user = create_user(role, nom, email, tele, password)
    if not user:
        return {"success": False, "message": "Erreur lors de la création du compte"}

    # Notification pour les admins si médecin
    if role == "medecin":
        for admin in Admin.get_all():
            socketio.emit(
                "notification",
                {"user_type": "admin", "user_id": admin.id, "message": f"Nouveau médecin inscrit: {nom}"},
                to=f"user_{admin.id}"
            )
        return {"success": True, "message": "Compte médecin créé avec succès, en attente d'approbation"}

    return {"success": True, "message": "Compte patient créé avec succès"}
def rpc_logout(params):
    logout_user()
    return {"success": True, "redirect": "/login"}


# ------------------- RPC HANDLER -------------------
@auth.route("/api/rpc", methods=["POST"])
def rpc_handler():
    data = request.get_json() or {}
    method = data.get("method")
    params = data.get("params", {})

    if method == "login":
        return jsonify(rpc_login(params))
    elif method == "register":
        return jsonify(rpc_register(params, role="patient"))
    elif method == "register_medecin":
        return jsonify(rpc_register(params, role="medecin"))
    elif method == "logout":
        return jsonify(rpc_logout(params))

    return jsonify({"success": False, "message": "Méthode RPC inconnue"}), 400
