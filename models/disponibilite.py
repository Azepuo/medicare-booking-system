# models/disponibilite.py
from database.connection import create_connection
from datetime import time

class Disponibilite:
    def __init__(self, id=None, medecin_id=None, jour_semaine=None, heure_debut=None, heure_fin=None):
        self.id = id
        self.medecin_id = medecin_id
        self.jour_semaine = jour_semaine
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin

    def to_dict(self):
        return {
            'id': self.id,
            'medecin_id': self.medecin_id,
            'jour_semaine': self.jour_semaine,
            'heure_debut': str(self.heure_debut) if self.heure_debut else None,
            'heure_fin': str(self.heure_fin) if self.heure_fin else None,
            'duree': self.calculer_duree()
        }

    def calculer_duree(self):
        """Calculer la durée"""
        if not self.heure_debut or not self.heure_fin:
            return "0h00"
        
        if isinstance(self.heure_debut, str):
            debut = time.fromisoformat(self.heure_debut)
            fin = time.fromisoformat(self.heure_fin)
        else:
            debut = self.heure_debut
            fin = self.heure_fin
            
        debut_minutes = debut.hour * 60 + debut.minute
        fin_minutes = fin.hour * 60 + fin.minute
        total_minutes = fin_minutes - debut_minutes
        
        heures = total_minutes // 60
        minutes = total_minutes % 60
        
        if minutes == 0:
            return f"{heures}h00"
        else:
            return f"{heures}h{minutes:02d}"

    @staticmethod
    def get_all(medecin_id=None):
        """Récupérer toutes les disponibilités"""
        conn = create_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            if medecin_id:
                cur.execute("SELECT * FROM disponibilites WHERE medecin_id = %s ORDER BY jour_semaine, heure_debut", (medecin_id,))
            else:
                cur.execute("SELECT * FROM disponibilites ORDER BY jour_semaine, heure_debut")
            rows = cur.fetchall()
            return [Disponibilite(**r) for r in rows]
        except Exception as e:
            print("Erreur get_all disponibilites:", e)
            return []
        finally:
            try: cur.close()
            except: pass
            try: conn.close()
            except: pass

    @staticmethod
    def get_by_id(dispo_id):
        """Récupérer une disponibilité par ID"""
        conn = create_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM disponibilites WHERE id = %s", (dispo_id,))
            row = cur.fetchone()
            return Disponibilite(**row) if row else None
        except Exception as e:
            print("Erreur get_by_id disponibilite:", e)
            return None
        finally:
            try: cur.close()
            except: pass
            try: conn.close()
            except: pass

    def save(self):
        """Sauvegarder la disponibilité (create or update)"""
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            if self.id:
                # Update
                cur.execute("""
                    UPDATE disponibilites 
                    SET medecin_id = %s, jour_semaine = %s, heure_debut = %s, heure_fin = %s
                    WHERE id = %s
                """, (self.medecin_id, self.jour_semaine, self.heure_debut, self.heure_fin, self.id))
            else:
                # Insert
                cur.execute("""
                    INSERT INTO disponibilites (medecin_id, jour_semaine, heure_debut, heure_fin)
                    VALUES (%s, %s, %s, %s)
                """, (self.medecin_id, self.jour_semaine, self.heure_debut, self.heure_fin))
                self.id = cur.lastrowid
            conn.commit()
            return True
        except Exception as e:
            try: conn.rollback()
            except: pass
            print("Erreur save disponibilite:", e)
            return False
        finally:
            try: cur.close()
            except: pass
            try: conn.close()
            except: pass

    def delete(self):
        """Supprimer la disponibilité"""
        if not self.id:
            return False
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM disponibilites WHERE id = %s", (self.id,))
            conn.commit()
            return True
        except Exception as e:
            try: conn.rollback()
            except: pass
            print("Erreur delete disponibilite:", e)
            return False
        finally:
            try: cur.close()
            except: pass
            try: conn.close()
            except: pass

    @staticmethod
    def check_conflit(medecin_id, jour_semaine, heure_debut, heure_fin, exclude_id=None):
        """Vérifier s'il y a un conflit avec des disponibilités existantes"""
        conn = create_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor(dictionary=True)
            if exclude_id:
                query = """
                    SELECT * FROM disponibilites 
                    WHERE medecin_id = %s AND jour_semaine = %s AND id != %s
                """
                params = (medecin_id, jour_semaine, exclude_id)
            else:
                query = """
                    SELECT * FROM disponibilites 
                    WHERE medecin_id = %s AND jour_semaine = %s
                """
                params = (medecin_id, jour_semaine)
            
            cur.execute(query, params)
            existing_dispos = cur.fetchall()
            
            for dispo in existing_dispos:
                existing_debut = dispo['heure_debut']
                existing_fin = dispo['heure_fin']
                
                # Vérifier le chevauchement
                if not (heure_fin <= existing_debut or heure_debut >= existing_fin):
                    return True
            
            return False
        except Exception as e:
            print("Erreur check_conflit:", e)
            return False
        finally:
            try: cur.close()
            except: pass
            try: conn.close()
            except: pass