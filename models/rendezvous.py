from database.connection_p import create_connection
from datetime import datetime

class RendezVous:
    def __init__(self, id=None, patient_id=None, medecin_id=None, date_heure=None, statut=None, notes=None):
        self.id = id
        self.patient_id = patient_id
        self.medecin_id = medecin_id
        self.date_heure = date_heure
        self.statut = statut or 'confirmé'
        self.notes = notes
    
    @staticmethod
    def get_all():
        """Récupérer tous les rendez-vous"""
        connection = create_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, p.nom as patient_nom, m.nom as medecin_nom 
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                JOIN medecins m ON r.medecin_id = m.id
            """)
            rendezvous = cursor.fetchall()
            return [RendezVous(**r) for r in rendezvous]
        except Exception as e:
            print(f"Erreur: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_by_id(rdv_id):
        """Récupérer un rendez-vous par son ID"""
        connection = create_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, p.nom as patient_nom, m.nom as medecin_nom 
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                JOIN medecins m ON r.medecin_id = m.id
                WHERE r.id = %s
            """, (rdv_id,))
            rdv_data = cursor.fetchone()
            return RendezVous(**rdv_data) if rdv_data else None
        except Exception as e:
            print(f"Erreur: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def get_by_patient(patient_id):
        """Récupérer les rendez-vous d'un patient"""
        connection = create_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM rendezvous WHERE patient_id = %s", (patient_id,))
            rendezvous = cursor.fetchall()
            return [RendezVous(**r) for r in rendezvous]
        except Exception as e:
            print(f"Erreur: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def get_by_medecin(medecin_id):
        """Récupérer les rendez-vous d'un médecin"""
        connection = create_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM rendezvous WHERE medecin_id = %s", (medecin_id,))
            rendezvous = cursor.fetchall()
            return [RendezVous(**r) for r in rendezvous]
        except Exception as e:
            print(f"Erreur: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def save(self):
        """Sauvegarder le rendez-vous"""
        connection = create_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            if self.id:
                # Update
                cursor.execute(
                    "UPDATE rendezvous SET patient_id = %s, medecin_id = %s, date_heure = %s, statut = %s, notes = %s WHERE id = %s",
                    (self.patient_id, self.medecin_id, self.date_heure, self.statut, self.notes, self.id)
                )
            else:
                # Create
                cursor.execute(
                    "INSERT INTO rendezvous (patient_id, medecin_id, date_heure, statut, notes) VALUES (%s, %s, %s, %s, %s)",
                    (self.patient_id, self.medecin_id, self.date_heure, self.statut, self.notes)
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

    def annuler(self):
        """Annuler le rendez-vous"""
        self.statut = 'annulé'
        return self.save()

    def __repr__(self):
        return f"<RendezVous {self.id}: Patient {self.patient_id} avec Medecin {self.medecin_id}>"