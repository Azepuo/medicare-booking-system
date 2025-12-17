from database.connection_m import create_connection


class Patient:
    def __init__(self, id=None, user_id=None, nom=None, email=None, telephone=None, sexe=None):
        self.id = id
        self.user_id = user_id
        self.nom = nom
        self.email = email
        self.telephone = telephone
        self.sexe = sexe

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nom": self.nom,
            "email": self.email,
            "telephone": self.telephone,
            "sexe": self.sexe
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
                SELECT id, user_id, nom, email, telephone, sexe
                FROM patients
                ORDER BY nom
            """)
            rows = cur.fetchall()
            return [Patient(**row) for row in rows]
        finally:
            cur.close()
            conn.close()

    # 🔹 GET BY ID
    @staticmethod
    def get_by_id(pid):
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT id, user_id, nom, email, telephone, sexe
                FROM patients
                WHERE id = %s
            """, (pid,))
            row = cur.fetchone()
            return Patient(**row) if row else None
        finally:
            cur.close()
            conn.close()

    # 🔹 SAVE (INSERT / UPDATE)
    def save(self):
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()

            if self.id:
                cur.execute("""
                    UPDATE patients
                    SET nom=%s, email=%s, telephone=%s, sexe=%s
                    WHERE id=%s
                """, (
                    self.nom,
                    self.email,
                    self.telephone,
                    self.sexe,
                    self.id
                ))
            else:
                cur.execute("""
                    INSERT INTO patients (user_id, nom, email, telephone, sexe)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    self.user_id,
                    self.nom,
                    self.email,
                    self.telephone,
                    self.sexe
                ))
                self.id = cur.lastrowid

            conn.commit()
            return True

        except Exception as e:
            print("❌ Erreur save patient:", e)
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
            cur.execute("DELETE FROM patients WHERE id=%s", (self.id,))
            conn.commit()
            return True
        except Exception as e:
            print("❌ Erreur delete patient:", e)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
