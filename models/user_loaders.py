from app.extensions import login_manager
from models.admin import Admin
from models.medecin import Medecin
from models.patient import Patient

@login_manager.user_loader
def load_user(user_id):
    """
    user_id = "prefix:id", ex: "admin:1", "medecin:3", "patient:5"
    """
    try:
        prefix, uid = user_id.split(":")
        uid = int(uid)
    except ValueError:
        return None

    if prefix == "admin":
        return Admin.get_by_id(uid)
    elif prefix == "medecin":
        return Medecin.get_by_id(uid)
    elif prefix == "patient":
        return Patient.get_by_id(uid)
    else:
        return None
