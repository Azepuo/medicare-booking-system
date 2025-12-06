from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(role):
    """
    Vérifie que l'utilisateur est connecté et possède le rôle requis.
    role: 'admin', 'medecin' ou 'patient'
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Veuillez vous connecter pour accéder à cette page.", "warning")
                return redirect(url_for("auth.login_page"))
            
            user_role = current_user.get_id().split(":")[0]
            if user_role != role:
                flash("Accès refusé : rôle non autorisé.", "danger")
                # Redirection selon rôle
                if user_role == "admin":
                    return redirect(url_for("admin.dashboard"))
                elif user_role == "medecin":
                    return redirect(url_for("medecin.dashboard"))
                elif user_role == "patient":
                    return redirect(url_for("patient.dashboard"))
                else:
                    return redirect(url_for("auth.login_page"))

            return f(*args, **kwargs)
        return wrapped
    return decorator
