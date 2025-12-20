from database.connection import create_connection
import bcrypt


class User:
    def __init__(self, nom, email, role, password=None, telephone=None, id=None):
        self.id = id
        self.nom = nom
        self.email = email
        self.password = password
        self.role = role
        self.telephone = telephone

    # =========================
    # 🔐 PASSWORD (bcrypt)
    # =========================
    def set_password(self, password):
        self.password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password):
        if not self.password:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password.encode("utf-8")
        )

    # =========================
    # 💾 SAVE (INSERT / UPDATE)
    # =========================
    def save(self):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        if self.id:  # UPDATE
            cursor.execute(
                """
                UPDATE users
                SET nom=%s, email=%s, password=%s, role=%s, telephone=%s
                WHERE id=%s
                """,
                (self.nom, self.email, self.password, self.role, self.telephone, self.id)
            )
        else:  # INSERT
            cursor.execute(
                """
                INSERT INTO users (nom, email, password, role, telephone)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (self.nom, self.email, self.password, self.role, self.telephone)
            )
            self.id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()
        return True

    # =========================
    # 🔍 GET BY EMAIL
    # =========================
    @classmethod
    def get_by_email(cls, email):
        conn = create_connection()
        if not conn:
            raise Exception("Impossible de se connecter à la base de données")

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, nom, email, password, role, telephone
            FROM users
            WHERE email=%s
            """,
            (email,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return None

        return cls(**row)

    # =========================
    # 🔍 GET BY ID
    # =========================
    @classmethod
    def get_by_id(cls, user_id):
        conn = create_connection()
        if not conn:
            raise Exception("Impossible de se connecter à la base de données")

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, nom, email, password, role, telephone
            FROM users
            WHERE id=%s
            """,
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return None

        return cls(**row)
