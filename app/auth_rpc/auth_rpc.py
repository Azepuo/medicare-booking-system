import re
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from app.extensions import db, socketio
from models.patient import Patient
from models.medecin import Medecin
from models.admin import Admin
from flask import session

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


# ------------------- Helper -------------------
def get_user_by_email(email):
    """
    Cherche un utilisateur dans les trois tables.
    """
    return (
        Patient.query.filter_by(email=email).first()
        or Medecin.query.filter_by(email=email).first()
        or Admin.query.filter_by(email=email).first()
    )


# ------------------- RPC LOGIN -------------------
def rpc_login(params):
    email = params.get("email", "").lower().strip()
    password = params.get("password", "")
    role = params.get("role", "patient").lower()

    if role == "patient":
        user = Patient.query.filter_by(email=email).first()

    elif role == "medecin":
        user = Medecin.query.filter_by(email=email).first()
        if user and not user.approved:
            return {"success": False, "message": "Compte médecin en attente d'approbation"}

    elif role == "admin":
        user = Admin.query.filter_by(email=email).first()

    else:
        return {"success": False, "message": "Rôle invalide"}

    # Vérification
    if not user or not check_password_hash(user.password, password):
        return {"success": False, "message": "Email ou mot de passe incorrect"}

    # Login (important → remember=False)
    login_user(user, remember=False)

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
    password = params.get("password", "")
    confirm = params.get("confirm_password", "")

    if not nom or not email or not password or not confirm:
        return {"success": False, "message": "Veuillez remplir tous les champs"}

    if password != confirm:
        return {"success": False, "message": "Les mots de passe ne correspondent pas"}

    if not re.match(EMAIL_REGEX, email):
        return {"success": False, "message": "Email invalide"}

    if get_user_by_email(email):
        return {"success": False, "message": "Email déjà utilisé"}


    user = Patient(nom=nom, email=email)
    user.password = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()

    return {"success": True, "message": "Compte patient créé avec succès"}


# ------------------- RPC REGISTER MÉDECIN -------------------

def rpc_register_medecin(params):

    nom = params.get("fullname", "").strip()
    email = params.get("email", "").strip().lower()
    password = params.get("password", "")
    confirm = params.get("confirm_password", "")

    if not nom or not email or not password or not confirm:
        return {"success": False, "message": "Veuillez remplir tous les champs"}

    if password != confirm:
        return {"success": False, "message": "Les mots de passe ne correspondent pas"}

    if not re.match(EMAIL_REGEX, email):
        return {"success": False, "message": "Email invalide"}

    if get_user_by_email(email):
        return {"success": False, "message": "Email déjà utilisé"}


    user = Medecin(nom=nom, email=email, approved=False)
    user.password = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()

    # Notifier tous les admins
    for admin in Admin.query.all():
        socketio.emit(
            "notification",
            {
                "user_type": "admin",
                "user_id": admin.id,
                "message": f"Nouveau médecin inscrit: {nom}"
            },
            to=f"user_{admin.id}"
        )

    return {"success": True, "message": "Compte médecin créé, en attente d'approbation"}


# ------------------- RPC LOGOUT -------------------

def rpc_logout(params):
    logout_user()
    session.clear()   # IMPORTANT !
    return {"success": True, "redirect": "/login"}
