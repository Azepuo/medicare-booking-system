# models/medecin.py
from database.connection import create_connection

class Medecin:
    def __init__(
        self,
        id=None,
        user_id=None,
        nom=None,
        email=None,
        telephone=None,
        id_specialisation=None,
        tarif_consultation=None,
        statut=None
    ):
        self.id = id
        self.user_id = user_id
        self.nom = nom
        self.email = email
        self.telephone = telephone
        self.id_specialisation = id_specialisation
        self.tarif_consultation = tarif_consultation
        self.statut = statut

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nom": self.nom,
            "email": self.email,
            "telephone": self.telephone,
            "id_specialisation": self.id_specialisation,
            "tarif_consultation": float(self.tarif_consultation) if self.tarif_consultation else None,
            "statut": self.statut
        }

    # -------------------------
    # RÉCUPÉRER TOUS LES MÉDECINS
    # -------------------------
    @staticmethod
    def get_all():
        conn = create_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM medecins ORDER BY nom")
            rows = cur.fetchall()
            return [Medecin(**row) for row in rows]
        finally:
            cur.close()
            conn.close()

    # -------------------------
    # RÉCUPÉRER PAR ID
    # -------------------------
    @staticmethod
    def get_by_id(medecin_id):
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM medecins WHERE id = %s", (medecin_id,))
            row = cur.fetchone()
            return Medecin(**row) if row else None
        finally:
            cur.close()
            conn.close()

    # -------------------------
    # RÉCUPÉRER PAR USER_ID
    # -------------------------
    @staticmethod
    def get_by_user_id(user_id):
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM medecins WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            return Medecin(**row) if row else None
        finally:
            cur.close()
            conn.close()

    # -------------------------
    # RÉCUPÉRER L'ID DU MÉDECIN PAR USER_ID
    # -------------------------
    @staticmethod
    def get_id_by_user_id(user_id):
        """Récupérer uniquement l'ID du médecin (medecins.id) à partir du user_id"""
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id FROM medecins WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            return row['id'] if row else None
        finally:
            cur.close()
            conn.close()

    # -------------------------
    # CRÉER UN MÉDECIN À PARTIR D'UN UTILISATEUR
    # -------------------------
    @staticmethod
    def create_from_user(user_id, nom, email, telephone='', id_specialisation=None, tarif_consultation=None):
        """Créer automatiquement un profil médecin pour un utilisateur"""
        conn = create_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO medecins (user_id, nom, email, telephone, id_specialisation, tarif_consultation, statut)
                VALUES (%s, %s, %s, %s, %s, %s, 'Actif')
            """, (user_id, nom, email, telephone, id_specialisation, tarif_consultation))
            
            medecin_id = cur.lastrowid
            conn.commit()
            
            # Récupérer le médecin créé
            return Medecin.get_by_id(medecin_id)
        except Exception as e:
            print(f"❌ Erreur création médecin: {e}")
            conn.rollback()
            return None
        finally:
            cur.close()
            conn.close()

    # -------------------------
    # SAUVEGARDER/METTRE À JOUR
    # -------------------------
    def save(self):
        """Sauvegarder ou mettre à jour un médecin"""
        conn = create_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            
            if self.id:
                # Mise à jour
                cur.execute("""
                    UPDATE medecins 
                    SET user_id=%s, nom=%s, email=%s, telephone=%s, 
                        id_specialisation=%s, tarif_consultation=%s, statut=%s
                    WHERE id=%s
                """, (
                    self.user_id, self.nom, self.email, self.telephone,
                    self.id_specialisation, self.tarif_consultation, self.statut,
                    self.id
                ))
            else:
                # Insertion
                cur.execute("""
                    INSERT INTO medecins 
                    (user_id, nom, email, telephone, id_specialisation, tarif_consultation, statut)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    self.user_id, self.nom, self.email, self.telephone,
                    self.id_specialisation, self.tarif_consultation, self.statut
                ))
                self.id = cur.lastrowid
            
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde médecin: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    # -------------------------
    # SUPPRIMER
    # -------------------------
    def delete(self):
        """Supprimer un médecin"""
        if not self.id:
            return False
        
        conn = create_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM medecins WHERE id = %s", (self.id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur suppression médecin: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    # -------------------------
    # VÉRIFIER SI UN MÉDECIN EXISTE POUR UN USER_ID
    # -------------------------
    @staticmethod
    def exists_by_user_id(user_id):
        """Vérifier si un profil médecin existe pour cet user_id"""
        conn = create_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) as count FROM medecins WHERE user_id = %s", (user_id,))
            result = cur.fetchone()
            return result['count'] > 0 if result else False
        finally:
            cur.close()
            conn.close()

    # -------------------------
    # RECHERCHER DES MÉDECINS
    # -------------------------
    @staticmethod
    def search(query):
        """Rechercher des médecins par nom ou email"""
        conn = create_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor(dictionary=True)
            search_term = f"%{query}%"
            cur.execute("""
                SELECT * FROM medecins 
                WHERE nom LIKE %s OR email LIKE %s 
                ORDER BY nom
            """, (search_term, search_term))
            rows = cur.fetchall()
            return [Medecin(**row) for row in rows]
        finally:
            cur.close()
            conn.close()