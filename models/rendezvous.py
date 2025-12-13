from database.connection_p import create_connection


class Rendezvous:
    def __init__(
        self,
        id=None,
        patient_id=None,
        medecin_id=None,
        date_rdv=None,
        heure_rdv=None,
        statut="en_attente",
        notes=None,
        patient_nom=None,
        medecin_nom=None
    ):
        self.id = id
        self.patient_id = patient_id
        self.medecin_id = medecin_id
        self.date_rdv = date_rdv
        self.heure_rdv = heure_rdv
        self.statut = statut
        self.notes = notes
        self.patient_nom = patient_nom
        self.medecin_nom = medecin_nom

    # ================= Utils =================
    def to_dict(self):
        return {
            "id": self.id,
            "date_rdv": str(self.date_rdv) if self.date_rdv else None,
            "heure_rdv": str(self.heure_rdv) if self.heure_rdv else None,
            "patient_id": self.patient_id,
            "patient_nom": self.patient_nom,
            "medecin_id": self.medecin_id,
            "medecin_nom": self.medecin_nom,
            "statut": self.statut,
            "notes": self.notes,
        }

    # ================= Getters =================
    @staticmethod
    def get_all():
        conn = create_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT r.*, p.nom AS patient_nom, m.nom AS medecin_nom
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                JOIN medecins m ON r.medecin_id = m.id
                ORDER BY r.date_rdv, r.heure_rdv
            """)
            rows = cur.fetchall()
            return [Rendezvous(**r) for r in rows]
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_id(rid):
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT r.*, p.nom AS patient_nom, m.nom AS medecin_nom
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                JOIN medecins m ON r.medecin_id = m.id
                WHERE r.id = %s
            """, (rid,))
            row = cur.fetchone()
            return Rendezvous(**row) if row else None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_patient(patient_id):
        conn = create_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT * FROM rendezvous
                WHERE patient_id = %s
                ORDER BY date_rdv, heure_rdv
            """, (patient_id,))
            rows = cur.fetchall()
            return [Rendezvous(**r) for r in rows]
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_medecin(medecin_id):
        conn = create_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT * FROM rendezvous
                WHERE medecin_id = %s
                ORDER BY date_rdv, heure_rdv
            """, (medecin_id,))
            rows = cur.fetchall()
            return [Rendezvous(**r) for r in rows]
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
                    UPDATE rendezvous
                    SET patient_id=%s, medecin_id=%s,
                        date_rdv=%s, heure_rdv=%s,
                        statut=%s, notes=%s
                    WHERE id=%s
                """, (
                    self.patient_id,
                    self.medecin_id,
                    self.date_rdv,
                    self.heure_rdv,
                    self.statut,
                    self.notes,
                    self.id
                ))
            else:
                cur.execute("""
                    INSERT INTO rendezvous
                        (patient_id, medecin_id, date_rdv, heure_rdv, statut, notes)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (
                    self.patient_id,
                    self.medecin_id,
                    self.date_rdv,
                    self.heure_rdv,
                    self.statut,
                    self.notes
                ))
                self.id = cur.lastrowid

            conn.commit()
            return True
        except Exception as e:
            print("Erreur Rendezvous.save():", e)
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
            cur.execute("DELETE FROM rendezvous WHERE id=%s", (self.id,))
            conn.commit()
            return True
        except Exception as e:
            print("Erreur Rendezvous.delete():", e)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    def annuler(self):
        self.statut = "annulé"
        return self.save()

    def __repr__(self):
        return f"<Rendezvous {self.id}: Patient {self.patient_id} - Medecin {self.medecin_id}>"
