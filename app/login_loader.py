from app.extensions import login_manager
from models.admin import Admin
from models.medecin import Medecin
from models.patient import Patient

@login_manager.user_loader
def load_user(user_id):
    if not user_id or ":" not in user_id:
        return None

    user_type, uid = user_id.split(":", 1)
    try:
        uid = int(uid)
    except ValueError:
        return None

    if user_type == "admin":
        return Admin.get_by_id(uid)
    elif user_type == "medecin":
        return Medecin.get_by_id(uid)
    elif user_type == "patient":
        return Patient.get_by_id(uid)
    return None
