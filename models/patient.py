from database.connection import create_connection

class Patient:
    def __init__(self, id=None, nom=None, email=None, telephone=None, date_inscription=None):
        self.id = id
        self.nom = nom
        self.email = email
        self.telephone = telephone
        self.date_inscription = date_inscription
    
    @staticmethod
    def get_all():
        """Récupérer tous les patients"""
        connection = create_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM patients")
            patients = cursor.fetchall()
            return [Patient(**p) for p in patients]
        except Exception as e:
            print(f"Erreur: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_by_id(patient_id):
        """Récupérer un patient par son ID"""
        connection = create_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
            patient_data = cursor.fetchone()
            return Patient(**patient_data) if patient_data else None
        except Exception as e:
            print(f"Erreur: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def save(self):
        """Sauvegarder le patient (create or update)"""
        connection = create_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            if self.id:
                # Update
                cursor.execute(
                    "UPDATE patients SET nom = %s, email = %s, telephone = %s WHERE id = %s",
                    (self.nom, self.email, self.telephone, self.id)
                )
            else:
                # Create
                cursor.execute(
                    "INSERT INTO patients (nom, email, telephone) VALUES (%s, %s, %s)",
                    (self.nom, self.email, self.telephone)
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

    def delete(self):
        """Supprimer le patient"""
        connection = create_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM patients WHERE id = %s", (self.id,))
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
        return f"<Patient {self.id}: {self.nom}>"