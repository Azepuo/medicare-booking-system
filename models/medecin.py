from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database.connection_p import create_connection


class Medecin(UserMixin):
    def __init__(
        self,
        id=None,
        nom=None,
        specialite=None,
        email=None,
        annees_experience=None,
        tarif_consultation=None,
        description=None,
        password=None,
        approved=False
    ):
        self.id = id
        self.nom = nom
        self.specialite = specialite
        self.email = email
        self.annees_experience = annees_experience
        self.tarif_consultation = tarif_consultation
        self.description = description
        self.password = password
        self.approved = approved

    # ================= Flask-Login =================
    def get_id(self):
        return f"medecin:{self.id}"

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    # ================= Utils =================
    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "specialite": self.specialite,
            "email": self.email,
            "annees_experience": self.annees_experience,
            "tarif_consultation": float(self.tarif_consultation)
            if self.tarif_consultation is not None else None,
            "description": self.description,
            "approved": self.approved
        }

    # ================= Getters =================
    @staticmethod
    def get_by_id(mid):
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM medecins WHERE id = %s", (mid,))
            row = cur.fetchone()
            return Medecin(**row) if row else None
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
            cur.execute("SELECT * FROM medecins WHERE email = %s", (email,))
            row = cur.fetchone()
            return Medecin(**row) if row else None
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
            cur.execute("SELECT * FROM medecins ORDER BY nom")
            rows = cur.fetchall()
            return [Medecin(**r) for r in rows]
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_specialite(specialite):
        conn = create_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM medecins WHERE specialite = %s ORDER BY nom",
                (specialite,)
            )
            rows = cur.fetchall()
            return [Medecin(**r) for r in rows]
        finally:
            cur.close()
            conn.close()

    # ================= Save =================
    def save(self):
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            if self.id:
                cur.execute("""
                    UPDATE medecins
                    SET nom=%s, specialite=%s, email=%s,
                        annees_experience=%s, tarif_consultation=%s,
                        description=%s, password=%s, approved=%s
                    WHERE id=%s
                """, (
                    self.nom, self.specialite, self.email,
                    self.annees_experience, self.tarif_consultation,
                    self.description, self.password,
                    self.approved, self.id
                ))
            else:
                cur.execute("""
                    INSERT INTO medecins
                        (nom, specialite, email, annees_experience,
                         tarif_consultation, description, password, approved)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    self.nom, self.specialite, self.email,
                    self.annees_experience, self.tarif_consultation,
                    self.description, self.password, self.approved
                ))
                self.id = cur.lastrowid

            conn.commit()
            return True
        except Exception as e:
            print("Erreur Medecin.save():", e)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    def __repr__(self):
        return f"<Medecin {self.id}: {self.nom} ({self.specialite})>"
