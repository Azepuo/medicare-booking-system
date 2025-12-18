from database.connection import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, nom, email, role, password=None, telephone=None, id=None):
        self.id = id
        self.nom = nom
        self.email = email
        self.password = password
        self.role = role
        self.telephone = telephone

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if self.id:  # update existant
            cursor.execute(
                "UPDATE users SET nom=%s, email=%s, password=%s, role=%s, telephone=%s WHERE id=%s",
                (self.nom, self.email, self.password, self.role, self.telephone, self.id)
            )
        else:  # insert nouveau
            cursor.execute(
                "INSERT INTO users (nom, email, password, role, telephone) VALUES (%s, %s, %s, %s, %s)",
                (self.nom, self.email, self.password, self.role, self.telephone)
            )
            self.id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()
        return True

    @classmethod
    def get_by_email(cls, email):
        conn = get_db_connection()
        if not conn:
            raise Exception("Impossible de se connecter à la base de données")
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nom, email, password, role, telephone FROM users WHERE email=%s",
            (email,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return None
        return cls(**row)

    @classmethod
    def get_by_id(cls, user_id):
        conn = get_db_connection()
        if not conn:
            raise Exception("Impossible de se connecter à la base de données")
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nom, email, password, role, telephone FROM users WHERE id=%s",
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return None
        return cls(**row)
