# models/rendezvous.py (correction)
from database.connection import create_connection

class Rendezvous:
    def __init__(
        self,
        id=None,
        date_heure=None,
        patient_id=None,
        user_id=None,  # Le médecin (via user_id)
        statut=None,
        notes=None,
        duree_consultation=None,
        type_consultation=None
    ):
        self.id = id
        self.date_heure = date_heure
        self.patient_id = patient_id
        self.user_id = user_id  # ← CORRIGÉ: user_id au lieu de medecin_id
        self.statut = statut
        self.notes = notes
        self.duree_consultation = duree_consultation
        self.type_consultation = type_consultation

    def to_dict(self):
        return {
            "id": self.id,
            "date_heure": self.date_heure.isoformat() if self.date_heure else None,
            "patient_id": self.patient_id,
            "user_id": self.user_id,  # ← CORRIGÉ
            "statut": self.statut,
            "notes": self.notes,
            "duree_consultation": self.duree_consultation,
            "type_consultation": self.type_consultation
        }

    @staticmethod
    def get_by_medecin_user_id(user_id, today_only=False):
        """Récupérer les RDV d'un médecin (par user_id)"""
        conn = create_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor(dictionary=True)
            
            if today_only:
                from datetime import date
                today = date.today()
                query = """
                    SELECT 
                        r.*,
                        p.nom as patient_nom,
                        p.telephone as patient_telephone,
                        p.email as patient_email
                    FROM rendez_vous r
                    LEFT JOIN patients p ON r.patient_id = p.id
                    WHERE r.user_id = %s 
                    AND DATE(r.date_heure) = %s
                    ORDER BY r.date_heure ASC
                """
                cur.execute(query, (user_id, today))
            else:
                query = """
                    SELECT 
                        r.*,
                        p.nom as patient_nom,
                        p.telephone as patient_telephone,
                        p.email as patient_email
                    FROM rendez_vous r
                    LEFT JOIN patients p ON r.patient_id = p.id
                    WHERE r.user_id = %s
                    ORDER BY r.date_heure DESC
                """
                cur.execute(query, (user_id,))
            
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()