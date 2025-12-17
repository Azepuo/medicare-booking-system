from database.connection_m import create_connection

class Medecin:
    def __init__(self, id=None, nom=None, specialite=None, email=None, annees_experience=None, tarif_consultation=None, description=None):
        self.id = id
        self.nom = nom
        self.specialite = specialite
        self.email = email
        self.annees_experience = annees_experience
        self.tarif_consultation = tarif_consultation
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'specialite': self.specialite,
            'email': self.email,
            'annees_experience': self.annees_experience,
            'tarif_consultation': float(self.tarif_consultation) if self.tarif_consultation else None,
            'description': self.description
        }

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
    def get_by_id(mid):
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM medecins WHERE id=%s", (mid,))
            row = cur.fetchone()
            return Medecin(**row) if row else None
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
            cur.execute("SELECT * FROM medecins WHERE specialite=%s ORDER BY nom", (specialite,))
            rows = cur.fetchall()
            return [Medecin(**r) for r in rows]
        finally:
            cur.close()
            conn.close()
