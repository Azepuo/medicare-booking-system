from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database.connection_p import create_connection


class Patient(UserMixin):
    def __init__(
        self,
        id=None,
        nom=None,
        email=None,
        telephone=None,
        password=None,
        date_inscription=None
    ):
        self.id = id
        self.nom = nom
        self.email = email
        self.telephone = telephone
        self.password = password
        self.date_inscription = date_inscription

    # ================= Flask-Login =================
    def get_id(self):
        return f"patient:{self.id}"

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    # ================= Utils =================
    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "email": self.email,
            "telephone": self.telephone,
            "date_inscription": str(self.date_inscription)
            if self.date_inscription else None
        }

    # ================= Getters =================
    @staticmethod
    def get_by_id(pid):
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM patients WHERE id=%s", (pid,))
            row = cur.fetchone()
            return Patient(**row) if row else None
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
            cur.execute("SELECT * FROM patients WHERE email=%s", (email,))
            row = cur.fetchone()
            return Patient(**row) if row else None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_all():
        conn = create_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM patients ORDER BY nom")
            rows = cur.fetchall()
            return [Patient(**r) for r in rows]
        finally:
            cur.close()
            conn.close()

    # ================= Save / Delete =================
    def save(self):
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            if self.id:
                cur.execute("""
                    UPDATE patients
                    SET nom=%s, email=%s, telephone=%s, password=%s
                    WHERE id=%s
                """, (self.nom, self.email, self.telephone, self.password, self.id))
            else:
                cur.execute("""
                    INSERT INTO patients (nom, email, telephone, password)
                    VALUES (%s, %s, %s, %s)
                """, (self.nom, self.email, self.telephone, self.password))
                self.id = cur.lastrowid

            conn.commit()
            return True
        except Exception as e:
            print("Erreur Patient.save():", e)
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
            cur.execute("DELETE FROM patients WHERE id=%s", (self.id,))
            conn.commit()
            return True
        except Exception as e:
            print("Erreur Patient.delete():", e)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    def __repr__(self):
        return f"<Patient {self.id}: {self.nom}>"
