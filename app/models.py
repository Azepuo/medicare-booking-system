from app.extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------- UTILISATEURS --------------------
class Patient(db.Model, UserMixin):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default="patient", nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)



class Medecin(db.Model, UserMixin):

    __tablename__ = "medecins"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default="medecin", nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)



class Admin(db.Model, UserMixin):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default="admin", nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# -------------------- NOTIFICATIONS --------------------
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------- USER LOADER --------------------
@login_manager.user_loader
def load_user(user_id):

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
