from database.connection_m import create_connection
from datetime import datetime


class Rendezvous:
    def __init__(self, id=None, date_heure=None, patient_id=None, medecin_id=None,
                 statut="En attente", notes=None, patient_nom=None, medecin_nom=None):
        self.id = id

        # Conversion sécurisée date_heure
        if isinstance(date_heure, str):
            try:
                self.date_heure = datetime.strptime(date_heure, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.date_heure = None
        else:
            self.date_heure = date_heure

        self.patient_id = patient_id
        self.medecin_id = medecin_id
        self.statut = statut
        self.notes = notes
        self.patient_nom = patient_nom
        self.medecin_nom = medecin_nom

    def to_dict(self):
        return {
            "id": self.id,
            "date_heure": self.date_heure.strftime("%Y-%m-%d %H:%M:%S") if self.date_heure else None,
            "patient_id": self.patient_id,
            "patient_nom": self.patient_nom,
            "medecin_id": self.medecin_id,
            "medecin_nom": self.medecin_nom,
            "statut": self.statut,
            "notes": self.notes
        }

    # 🔹 GET ALL
    @staticmethod
    def get_all():
        conn = create_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT r.id, r.date_heure, r.patient_id, r.medecin_id,
                       r.statut, r.notes,
                       p.nom AS patient_nom,
                       m.nom AS medecin_nom
                FROM rendezvous r
                LEFT JOIN patients p ON r.patient_id = p.id
                LEFT JOIN medecins m ON r.medecin_id = m.id
                ORDER BY r.date_heure
            """)
            rows = cur.fetchall()
            return [Rendezvous(**row) for row in rows]
        finally:
            cur.close()
            conn.close()

    # 🔹 GET BY ID
    @staticmethod
    def get_by_id(rid):
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT r.id, r.date_heure, r.patient_id, r.medecin_id,
                       r.statut, r.notes,
                       p.nom AS patient_nom,
                       m.nom AS medecin_nom
                FROM rendezvous r
                LEFT JOIN patients p ON r.patient_id = p.id
                LEFT JOIN medecins m ON r.medecin_id = m.id
                WHERE r.id = %s
            """, (rid,))
            row = cur.fetchone()
            return Rendezvous(**row) if row else None
        finally:
            cur.close()
            conn.close()

    # 🔹 SAVE
    def save(self):
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            date_val = self.date_heure.strftime("%Y-%m-%d %H:%M:%S") if self.date_heure else None

            if self.id:
                cur.execute("""
                    UPDATE rendezvous
                    SET date_heure=%s, patient_id=%s, medecin_id=%s, statut=%s, notes=%s
                    WHERE id=%s
                """, (
                    date_val,
                    self.patient_id,
                    self.medecin_id,
                    self.statut,
                    self.notes,
                    self.id
                ))
            else:
                cur.execute("""
                    INSERT INTO rendezvous (date_heure, patient_id, medecin_id, statut, notes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    date_val,
                    self.patient_id,
                    self.medecin_id,
                    self.statut,
                    self.notes
                ))
                self.id = cur.lastrowid

            conn.commit()
            return True

        except Exception as e:
            print("❌ Erreur save rendezvous:", e)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    # 🔹 DELETE
    def delete(self):
        if not self.id:
            return False
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM rendezvous WHERE id=%s", (self.id,))
            conn.commit()
            return True
        except Exception as e:
            print("❌ Erreur delete rendezvous:", e)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    # 🔹 ANNULER
    def annuler(self):
        self.statut = "Annulé"
        return self.save()
