from database.connection import create_connection
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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
        password=None
    ):
        self.id = id
        self.nom = nom
        self.specialite = specialite
        self.email = email
        self.annees_experience = annees_experience
        self.tarif_consultation = tarif_consultation
        self.description = description
        self.password = password

    
    # ------------------ Flask-Login ------------------
    def get_id(self):
        return f"medecin:{self.id}"

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    # --------------------- GETTERS -------------------
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
    def get_all():
        conn = create_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM medecins")
            rows = cur.fetchall()
            return [Medecin(**m) for m in rows]
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
            cur.execute("SELECT * FROM medecins WHERE specialite = %s", (specialite,))
            rows = cur.fetchall()
            return [Medecin(**m) for m in rows]
        finally:
            cur.close()
            conn.close()

    # ---------------------- SAVE ---------------------
    def save(self):
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            if self.id:
                # UPDATE
                cur.execute("""
                    UPDATE medecins 
                    SET nom=%s, specialite=%s, email=%s, annees_experience=%s, tarif_consultation=%s,
                        description=%s, password=%s
                    WHERE id=%s
                """, (
                    self.nom, self.specialite, self.email, self.annees_experience,
                    self.tarif_consultation, self.description, self.password,self.id
                ))
            else:
                # INSERT
                cur.execute("""
                    INSERT INTO medecins 
                        (nom, specialite, email, annees_experience, tarif_consultation, description, password)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (
                    self.nom, self.specialite, self.email, self.annees_experience,
                    self.tarif_consultation, self.description, self.password
                ))
                self.id = cur.lastrowid

            conn.commit()
            return True
        except Exception as e:
            print("Erreur medecin.save():", e)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    def __repr__(self):
        return f"<Medecin {self.id}: {self.nom} ({self.specialite})>"
