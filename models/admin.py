from database.connection import create_connection
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(UserMixin):
    def __init__(self, id=None, nom=None, email=None, password=None, date_inscription=None):
        self.id = id
        self.nom = nom
        self.email = email
        self.password = password  # stocké hashé
        self.date_inscription = date_inscription

    # ---------------- Flask-Login ----------------
    def get_id(self):
        # On préfixe pour distinguer le type d'utilisateur
        return f"admin:{self.id}"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # ---------------- Méthodes DB ----------------
    @staticmethod
    def get_all():
        conn = create_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id, nom, email, password, date_inscription FROM admins ORDER BY nom")
            rows = cur.fetchall()
            return [Admin(**r) for r in rows]
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_id(pid):
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id, nom, email, password, date_inscription FROM admins WHERE id=%s", (pid,))
            row = cur.fetchone()
            return Admin(**row) if row else None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_email(email):
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id, nom, email, password, date_inscription FROM admins WHERE email=%s", (email,))
            row = cur.fetchone()
            return Admin(**row) if row else None
        finally:
            cur.close()
            conn.close()

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def save(self):
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            if self.id:
                cur.execute(
                    "UPDATE admins SET nom=%s, email=%s, password=%s WHERE id=%s",
                    (self.nom, self.email, self.password, self.id)
                )
            else:
                cur.execute(
                    "INSERT INTO admins (nom, email, password) VALUES (%s, %s, %s)",
                    (self.nom, self.email, self.password)
                )
                self.id = cur.lastrowid
            conn.commit()
            return True
        except Exception as e:
            print("Erreur save admin:", e)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    def delete(self):
        if not self.id:
            return False
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM admins WHERE id=%s", (self.id,))
            conn.commit()
            return True
        except Exception as e:
            print("Erreur delete admin:", e)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
