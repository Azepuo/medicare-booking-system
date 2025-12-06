from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user
from app.extensions import socketio
from models.patient import Patient
from models.medecin import Medecin
from models.admin import Admin
import re

auth = Blueprint("auth", __name__, template_folder="templates/auth")

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

# ------------------ LOGIN PAGE ------------------
@auth.route("/login", methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        role = current_user.get_id().split(":")[0]
        return redirect(url_for(f"{role}.dashboard"))
    return render_template("auth/login.html")


# ------------------ REGISTER PAGE ------------------
@auth.route("/register", methods=["GET"])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for("patient.dashboard"))
    return render_template("auth/register.html")


# ------------------ LOGOUT ------------------
@auth.route("/logout")
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("auth.login_page"))


# ------------------- Helper -------------------
def get_user_by_email(email):
    """Cherche un utilisateur dans les trois tables"""
    return Patient.get_by_email(email) or Medecin.get_by_email(email) or Admin.get_by_email(email)


# ------------------- RPC LOGIN -------------------
def rpc_login(params):
    email = params.get("email", "").lower().strip()
    password = params.get("password", "")
    role = params.get("role", "patient").lower()

    if role == "patient":
        user = Patient.get_by_email(email)
    elif role == "medecin":
        user = Medecin.get_by_email(email)
        if user and getattr(user, "approved", False) is False:
            return {"success": False, "message": "Compte médecin en attente d'approbation"}
    elif role == "admin":
        user = Admin.get_by_email(email)
    else:
        return {"success": False, "message": "Rôle invalide"}

    # ✅ Vérification sécurisée du mot de passe
    if not user or not user.check_password(password):

        return {"success": False, "message": "Email ou mot de passe incorrect"}

    login_user(user)
    redirect_map = {
        "patient": "/patient/dashboard",
        "medecin": "/medecin/dashboard",
        "admin": "/admin/dashboard"
    }
    return {"success": True, "redirect": redirect_map.get(role, "/")}


# ------------------- RPC REGISTER PATIENT -------------------
def rpc_register(params):
    nom = params.get("fullname", "").strip()
    email = params.get("email", "").strip().lower()
    tele = params.get("tele", "").strip()
    password = params.get("password", "")
    confirm = params.get("confirm_password", "")

    if not nom or not email or not tele or not password or not confirm:
        return {"success": False, "message": "Veuillez remplir tous les champs"}

    if password != confirm:
        return {"success": False, "message": "Les mots de passe ne correspondent pas"}

    if not re.match(EMAIL_REGEX, email):
        return {"success": False, "message": "Email invalide"}

    if get_user_by_email(email):
        return {"success": False, "message": "Email déjà utilisé"}

    user = Patient(nom=nom, email=email, telephone=tele)
    user.set_password(password)
    if not user.save():
        return {"success": False, "message": "Erreur lors de la création du compte"}

    return {"success": True, "message": "Compte patient créé avec succès"}


# ------------------- RPC REGISTER MÉDECIN -------------------
def rpc_register_medecin(params):
    nom = params.get("fullname", "").strip()
    email = params.get("email", "").strip().lower()
    tele = params.get("tele", "").strip()
    password = params.get("password", "")
    confirm = params.get("confirm_password", "")

    if not nom or not email or not tele or not password or not confirm:
        return {"success": False, "message": "Veuillez remplir tous les champs"}

    if password != confirm:
        return {"success": False, "message": "Les mots de passe ne correspondent pas"}

    if not re.match(EMAIL_REGEX, email):
        return {"success": False, "message": "Email invalide"}

    if get_user_by_email(email):
        return {"success": False, "message": "Email déjà utilisé"}

    user = Medecin(nom=nom, email=email, telephone=tele, approved=False)
    user.set_password(password)
    if not user.save():
        return {"success": False, "message": "Erreur lors de la création du compte"}

    # Notification pour les admins
    for admin in Admin.get_all():
        socketio.emit(
            "notification",
            {"user_type": "admin", "user_id": admin.id, "message": f"Nouveau médecin inscrit: {nom}"},
            to=f"user_{admin.id}"
        )

    return {"success": True, "message": "Compte médecin créé avec succès, en attente d'approbation"}


# ------------------- RPC LOGOUT -------------------
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
        return jsonify(rpc_register(params))
    elif method == "register_medecin":
        return jsonify(rpc_register_medecin(params))
    elif method == "logout":
        return jsonify(rpc_logout(params))

    return jsonify({"success": False, "message": "Méthode RPC inconnue"}), 400
