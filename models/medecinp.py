from database.connection import get_db_connection

class Medecin:
    def __init__(self, id=None, nom=None, specialite=None, email=None, annees_experience=None, tarif_consultation=None, description=None):
        self.id = id
        self.nom = nom
        self.specialite = specialite
        self.email = email
        self.annees_experience = annees_experience
        self.tarif_consultation = tarif_consultation
        self.description = description
    
    @staticmethod
    def get_all():
        """Récupérer tous les médecins"""
        connection = get_db_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM medecins")
            medecins = cursor.fetchall()
            return [Medecin(**m) for m in medecins]
        except Exception as e:
            print(f"Erreur: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_by_id(medecin_id):
        """Récupérer un médecin par son ID"""
        connection = get_db_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM medecins WHERE id = %s", (medecin_id,))
            medecin_data = cursor.fetchone()
            return Medecin(**medecin_data) if medecin_data else None
        except Exception as e:
            print(f"Erreur: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def get_by_specialite(specialite):
        """Récupérer les médecins par spécialité"""
        connection = get_db_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM medecins WHERE specialite = %s", (specialite,))
            medecins = cursor.fetchall()
            return [Medecin(**m) for m in medecins]
        except Exception as e:
            print(f"Erreur: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def save(self):
        """Sauvegarder le médecin (create or update)"""
        connection = get_db_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            if self.id:
                # Update
                cursor.execute(
                    "UPDATE medecins SET nom = %s, specialite = %s, email = %s, annees_experience = %s, tarif_consultation = %s, description = %s WHERE id = %s",
                    (self.nom, self.specialite, self.email, self.annees_experience, self.tarif_consultation, self.description, self.id)
                )
            else:
                # Create
                cursor.execute(
                    "INSERT INTO medecins (nom, specialite, email, annees_experience, tarif_consultation, description) VALUES (%s, %s, %s, %s, %s, %s)",
                    (self.nom, self.specialite, self.email, self.annees_experience, self.tarif_consultation, self.description)
                )
                self.id = cursor.lastrowid
            
            connection.commit()
            return True
        except Exception as e:
            print(f"Erreur: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def __repr__(self):
        return f"<Medecin {self.id}: {self.nom} ({self.specialite})>"