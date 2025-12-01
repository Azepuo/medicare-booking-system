from database.connection import create_connection

class Patient:
    def __init__(self, id=None, nom=None, email=None, telephone=None, date_inscription=None):
        self.id = id
        self.nom = nom
        self.email = email
        self.telephone = telephone
        self.date_inscription = date_inscription

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'email': self.email,
            'telephone': self.telephone,
            'date_inscription': str(self.date_inscription) if self.date_inscription else None
        }

    @staticmethod
    def get_all():
        conn = create_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id, nom, email, telephone, date_inscription FROM patients ORDER BY nom")
            rows = cur.fetchall()
            return [Patient(**r) for r in rows]
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
            cur.execute("SELECT id, nom, email, telephone, date_inscription FROM patients WHERE id=%s", (pid,))
            row = cur.fetchone()
            return Patient(**row) if row else None
        finally:
            cur.close()
            conn.close()

    def save(self):
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            if self.id:
                cur.execute("UPDATE patients SET nom=%s, email=%s, telephone=%s WHERE id=%s",
                            (self.nom, self.email, self.telephone, self.id))
            else:
                cur.execute("INSERT INTO patients (nom, email, telephone) VALUES (%s,%s,%s)",
                            (self.nom, self.email, self.telephone))
                self.id = cur.lastrowid
            conn.commit()
            return True
        except Exception as e:
            print("Erreur save patient:", e)
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
            print("Erreur delete patient:", e)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()