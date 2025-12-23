# models/disponibilite.py
from database.connection import create_connection

class Disponibilite:
    def __init__(self, id=None, medecin_id=None, jour_semaine=None, heure_debut=None, heure_fin=None):
        self.id = id
        self.medecin_id = medecin_id  # CHANGÉ: user_id -> medecin_id
        self.jour_semaine = jour_semaine
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin

    def save(self):
        conn = create_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            if self.id:
                # Mise à jour
                cursor.execute("""
                    UPDATE disponibilites 
                    SET jour_semaine = %s, heure_debut = %s, heure_fin = %s
                    WHERE id = %s AND medecin_id = %s
                """, (self.jour_semaine, self.heure_debut, self.heure_fin, self.id, self.medecin_id))
            else:
                # Insertion
                cursor.execute("""
                    INSERT INTO disponibilites (medecin_id, jour_semaine, heure_debut, heure_fin)
                    VALUES (%s, %s, %s, %s)
                """, (self.medecin_id, self.jour_semaine, self.heure_debut, self.heure_fin))
                self.id = cursor.lastrowid
            
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur save Disponibilite: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def delete(self):
        conn = create_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM disponibilites WHERE id = %s AND medecin_id = %s", 
                          (self.id, self.medecin_id))  # CHANGÉ: user_id -> medecin_id
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Erreur delete Disponibilite: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_id(dispo_id, medecin_id=None):
        conn = create_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            if medecin_id:
                cursor.execute("SELECT * FROM disponibilites WHERE id = %s AND medecin_id = %s", 
                             (dispo_id, medecin_id))  # CHANGÉ: user_id -> medecin_id
            else:
                cursor.execute("SELECT * FROM disponibilites WHERE id = %s", (dispo_id,))
            
            row = cursor.fetchone()
            if row:
                return Disponibilite(
                    id=row['id'],
                    medecin_id=row['medecin_id'],  # CHANGÉ: user_id -> medecin_id
                    jour_semaine=row['jour_semaine'],
                    heure_debut=row['heure_debut'],
                    heure_fin=row['heure_fin']
                )
            return None
        except Exception as e:
            print(f"❌ Erreur get_by_id Disponibilite: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_by_medecin(medecin_id, jour_semaine=None):
        conn = create_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            if jour_semaine:
                cursor.execute("""
                    SELECT * FROM disponibilites 
                    WHERE medecin_id = %s AND jour_semaine = %s
                    ORDER BY 
                        FIELD(jour_semaine, 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'),
                        heure_debut
                """, (medecin_id, jour_semaine))  # CHANGÉ: user_id -> medecin_id
            else:
                cursor.execute("""
                    SELECT * FROM disponibilites 
                    WHERE medecin_id = %s
                    ORDER BY 
                        FIELD(jour_semaine, 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'),
                        heure_debut
                """, (medecin_id,))  # CHANGÉ: user_id -> medecin_id
            
            rows = cursor.fetchall()
            disponibilites = []
            for row in rows:
                disponibilites.append(Disponibilite(
                    id=row['id'],
                    medecin_id=row['medecin_id'],  # CHANGÉ: user_id -> medecin_id
                    jour_semaine=row['jour_semaine'],
                    heure_debut=row['heure_debut'],
                    heure_fin=row['heure_fin']
                ))
            return disponibilites
        except Exception as e:
            print(f"❌ Erreur get_all_by_medecin Disponibilite: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all():
        conn = create_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM disponibilites 
                ORDER BY medecin_id, jour_semaine, heure_debut
            """)
            
            rows = cursor.fetchall()
            disponibilites = []
            for row in rows:
                disponibilites.append(Disponibilite(
                    id=row['id'],
                    medecin_id=row['medecin_id'],  # CHANGÉ: user_id -> medecin_id
                    jour_semaine=row['jour_semaine'],
                    heure_debut=row['heure_debut'],
                    heure_fin=row['heure_fin']
                ))
            return disponibilites
        except Exception as e:
            print(f"❌ Erreur get_all Disponibilite: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def to_dict(self):
        return {
            'id': self.id,
            'medecin_id': self.medecin_id,  # CHANGÉ: user_id -> medecin_id
            'jour_semaine': self.jour_semaine,
            'heure_debut': str(self.heure_debut) if self.heure_debut else None,
            'heure_fin': str(self.heure_fin) if self.heure_fin else None
        }