from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from app.extensions import db, socketio
from app.models import Patient, Medecin, Admin, Notification
import re

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

def find_user_by_email(email):
    return Patient.query.filter_by(email=email).first() \
        or Medecin.query.filter_by(email=email).first() \
        or Admin.query.filter_by(email=email).first()

def rpc_login(params):
    email = params.get("email", "").lower().strip()
    password = params.get("password", "")
    if not email or not password:
        return jsonify({"success": False, "message": "Email et mot de passe requis"})
    user = find_user_by_email(email)
    if not user or not check_password_hash(user.password, password):
        return jsonify({"success": False, "message": "Email ou mot de passe incorrect"})
    if isinstance(user, Medecin) and not user.approved:
        return jsonify({"success": False, "message": "Compte médecin en attente d’approbation"})
    login_user(user)
    return jsonify({"success": True, "role": user.role, "redirect": f"/{user.role}/dashboard"})

def rpc_register(params):
    nom = params.get("fullname", "").strip()
    email = params.get("email", "").lower().strip()
    password = params.get("password", "")
    confirm = params.get("confirm_password", "")
    role = params.get("role", "").lower() or "patient"

    if not nom or not email or not password or not confirm:
        return jsonify({"success": False, "message": "Tous les champs sont obligatoires"})
    if password != confirm:
        return jsonify({"success": False, "message": "Les mots de passe ne correspondent pas"})
    if not re.match(EMAIL_REGEX, email):
        return jsonify({"success": False, "message": "Email invalide"})
    if find_user_by_email(email):
        return jsonify({"success": False, "message": "Email déjà utilisé"})

    if role == "patient":
        user = Patient(nom=nom, email=email)
    elif role == "medecin":
        user = Medecin(nom=nom, email=email, approved=False)
        # notification aux admins
        for admin in Admin.query.all():
            note = Notification(user_type="admin", user_id=admin.id,
                                message=f"Nouveau médecin inscrit: {nom}")
            db.session.add(note)
            socketio.emit("notification", {
                "user_type": "admin",
                "user_id": admin.id,
                "message": note.message
            }, to=f"user_{admin.id}")
    elif role == "admin":
        user = Admin(nom=nom, email=email)
    else:
        return jsonify({"success": False, "message": "Rôle invalide"})

    user.password = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True, "message": f"Compte {role} créé avec succès"})

def rpc_logout(params):
    logout_user()
    return jsonify({"success": True, "message": "Déconnexion réussie", "redirect": "/login"})
