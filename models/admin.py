from app.extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime


class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Méthodes sécurisées ---
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # Flask-Login
    def get_id(self):
        return f"admin-{self.id}"
