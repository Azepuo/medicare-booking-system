from app.extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------------------------
# MODELE UTILISATEUR : Patient
# -------------------------------------
class Patient(db.Model, UserMixin):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    role = "patient"

    def get_id(self):
        return f"patient-{self.id}"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# -------------------------------------
# MODELE UTILISATEUR : Medecin
# -------------------------------------
class Medecin(db.Model, UserMixin):
    __tablename__ = "medecins"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    
    # Colonnes supplémentaires pour le médecin
    annees_experience = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    specialite = db.Column(db.String(100), nullable=True)
    tarif_consultation = db.Column(db.Float, nullable=True)

    role = "medecin"

    def get_id(self):
        return f"medecin-{self.id}"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# -------------------------------------
# MODELE UTILISATEUR : Admin
# -------------------------------------
class Admin(db.Model, UserMixin):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    role = "admin"

    def get_id(self):
        return f"admin-{self.id}"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# ---------------------------------------------------
# USER LOADER (Flask Login)
# ---------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    """
    Charge user_id sous forme :
    patient-1
    medecin-3
    admin-1
    """
    try:
        role, real_id = user_id.split("-")
        real_id = int(real_id)
    except:
        return None

    if role == "patient":
        return Patient.query.get(real_id)
    elif role == "medecin":
        return Medecin.query.get(real_id)
    elif role == "admin":
        return Admin.query.get(real_id)

    return None
