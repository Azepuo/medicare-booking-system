# models/rendezvous.py (correction complète)
from database.connection import create_connection
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class Rendezvous:
    def __init__(
        self,
        id=None,
        date_heure=None,
        patient_id=None,
        medecin_id=None,  # ✅ Changé de user_id à medecin_id
        statut=None,
        notes=None,
        patient_nom=None,     # Champ additionnel pour le nom du patient
        patient_prenom=None,  # Champ additionnel pour le prénom du patient
        patient_telephone=None, # Champ additionnel pour le téléphone
        patient_email=None    # Champ additionnel pour l'email
    ):
        self.id = id
        self.date_heure = date_heure
        self.patient_id = patient_id
        self.medecin_id = medecin_id  # ✅ Changé de user_id à medecin_id
        self.statut = statut
        self.notes = notes
        self.patient_nom = patient_nom
        self.patient_prenom = patient_prenom
        self.patient_telephone = patient_telephone
        self.patient_email = patient_email

    def to_dict(self):
        """Convertir l'objet en dictionnaire pour JSON"""
        # Formater la date pour l'affichage
        date_heure_formatted = None
        date_heure_display = None
        
        if self.date_heure:
            if isinstance(self.date_heure, (datetime, date)):
                date_heure_formatted = self.date_heure.isoformat()
                date_heure_display = self.date_heure.strftime('%Y-%m-%d %H:%M')
                # Format pour input datetime-local
                date_heure_input = self.date_heure.strftime('%Y-%m-%dT%H:%M')
            else:
                date_heure_formatted = self.date_heure
                date_heure_display = self.date_heure
                date_heure_input = self.date_heure
        
        # Nom complet du patient
        patient_nom_complet = ""
        if self.patient_prenom and self.patient_nom:
            patient_nom_complet = f"{self.patient_prenom} {self.patient_nom}"
        elif self.patient_nom:
            patient_nom_complet = self.patient_nom
        
        return {
            "id": self.id,
            "date_heure": date_heure_formatted,
            "date_heure_display": date_heure_display,
            "date_heure_input": date_heure_input if 'date_heure_input' in locals() else date_heure_formatted,
            "patient_id": self.patient_id,
            "medecin_id": self.medecin_id,  # ✅ Changé de user_id à medecin_id
            "statut": self.statut,
            "notes": self.notes,
            "patient_nom": self.patient_nom,
            "patient_prenom": self.patient_prenom,
            "patient_nom_complet": patient_nom_complet,
            "patient_telephone": self.patient_telephone,
            "patient_email": self.patient_email
        }

    @staticmethod
    def get_by_medecin_id(medecin_id, today_only=False):
        """Récupérer les RDV d'un médecin (par medecin_id)"""
        conn = create_connection()
        if not conn:
            logger.error("Échec de connexion à la base de données")
            return []
        
        try:
            cur = conn.cursor(dictionary=True)
            
            if today_only:
                today = date.today()
                query = """
                    SELECT 
                        r.*,
                        p.nom as patient_nom,
                        p.prenom as patient_prenom,
                        p.telephone as patient_telephone,
                        p.email as patient_email
                    FROM rendezvous r
                    LEFT JOIN patients p ON r.patient_id = p.id
                    WHERE r.medecin_id = %s  -- ✅ Changé user_id à medecin_id
                    AND DATE(r.date_heure) = %s
                    ORDER BY r.date_heure ASC
                """
                cur.execute(query, (medecin_id, today))
            else:
                query = """
                    SELECT 
                        r.*,
                        p.nom as patient_nom,
                        p.prenom as patient_prenom,
                        p.telephone as patient_telephone,
                        p.email as patient_email
                    FROM rendezvous r
                    LEFT JOIN patients p ON r.patient_id = p.id
                    WHERE r.medecin_id = %s  -- ✅ Changé user_id à medecin_id
                    ORDER BY r.date_heure DESC
                """
                cur.execute(query, (medecin_id,))
            
            rows = cur.fetchall()
            
            # Convertir les résultats en instances de Rendezvous
            rdvs = []
            for row in rows:
                rdv = Rendezvous(
                    id=row['id'],
                    date_heure=row['date_heure'],
                    patient_id=row['patient_id'],
                    medecin_id=row['medecin_id'],  # ✅ Changé de user_id à medecin_id
                    statut=row['statut'],
                    notes=row.get('notes'),
                    patient_nom=row.get('patient_nom'),
                    patient_prenom=row.get('patient_prenom'),
                    patient_telephone=row.get('patient_telephone'),
                    patient_email=row.get('patient_email')
                )
                rdvs.append(rdv)
            
            logger.info(f"Récupéré {len(rdvs)} rendez-vous pour le médecin ID {medecin_id}")
            return rdvs
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des rendez-vous: {e}")
            return []
        finally:
            if 'cur' in locals():
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def get_by_user_id(user_id, today_only=False):
        """Récupérer les RDV d'un médecin via son user_id (conversion automatique)"""
        # D'abord, récupérer l'ID du médecin à partir du user_id
        medecin_id = Rendezvous._get_medecin_id_from_user_id(user_id)
        if not medecin_id:
            logger.error(f"Pas de médecin trouvé pour user_id {user_id}")
            return []
        
        # Utiliser la méthode existante avec medecin_id
        return Rendezvous.get_by_medecin_id(medecin_id, today_only)

    @staticmethod
    def _get_medecin_id_from_user_id(user_id):
        """Helper pour récupérer l'ID du médecin à partir du user_id"""
        conn = create_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor(dictionary=True)
            query = "SELECT id FROM medecins WHERE user_id = %s"
            cur.execute(query, (user_id,))
            row = cur.fetchone()
            
            if row:
                return row['id']
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du médecin: {e}")
            return None
        finally:
            if 'cur' in locals():
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def get_by_id_and_medecin(rdv_id, medecin_id):
        """Récupérer un rendez-vous spécifique par son ID et le medecin_id"""
        conn = create_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    r.*,
                    p.nom as patient_nom,
                    p.prenom as patient_prenom,
                    p.telephone as patient_telephone,
                    p.email as patient_email
                FROM rendezvous r
                LEFT JOIN patients p ON r.patient_id = p.id
                WHERE r.id = %s AND r.medecin_id = %s  -- ✅ Changé user_id à medecin_id
            """
            cur.execute(query, (rdv_id, medecin_id))
            row = cur.fetchone()
            
            if row:
                return Rendezvous(
                    id=row['id'],
                    date_heure=row['date_heure'],
                    patient_id=row['patient_id'],
                    medecin_id=row['medecin_id'],  # ✅ Changé de user_id à medecin_id
                    statut=row['statut'],
                    notes=row.get('notes'),
                    patient_nom=row.get('patient_nom'),
                    patient_prenom=row.get('patient_prenom'),
                    patient_telephone=row.get('patient_telephone'),
                    patient_email=row.get('patient_email')
                )
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du rendez-vous: {e}")
            return None
        finally:
            if 'cur' in locals():
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def get_by_id_and_user_id(rdv_id, user_id):
        """Récupérer un rendez-vous spécifique par son ID et le user_id"""
        # D'abord, récupérer l'ID du médecin
        medecin_id = Rendezvous._get_medecin_id_from_user_id(user_id)
        if not medecin_id:
            return None
        
        # Utiliser la méthode existante
        return Rendezvous.get_by_id_and_medecin(rdv_id, medecin_id)

    @staticmethod
    def create(patient_id, medecin_id, date_heure, statut="En attente", notes=None):
        """Créer un nouveau rendez-vous"""
        conn = create_connection()
        if not conn:
            logger.error("Échec de connexion à la base de données")
            return None
        
        try:
            # Formater la date si nécessaire
            if 'T' in date_heure:
                date_heure = date_heure.replace('T', ' ')
            if date_heure.endswith('Z'):
                date_heure = date_heure[:-1]
            
            # Vérifier la disponibilité
            check_query = """
                SELECT id FROM rendezvous 
                WHERE medecin_id = %s AND date_heure = %s
            """
            cur = conn.cursor(dictionary=True)
            cur.execute(check_query, (medecin_id, date_heure))
            existing = cur.fetchone()
            
            if existing:
                raise Exception("Ce créneau est déjà réservé pour ce médecin")
            
            # Insérer le rendez-vous
            query = """
                INSERT INTO rendezvous 
                (patient_id, medecin_id, date_heure, statut, notes)
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query, (patient_id, medecin_id, date_heure, statut, notes))
            conn.commit()
            
            rdv_id = cur.lastrowid
            logger.info(f"Rendez-vous créé avec ID {rdv_id} pour le médecin {medecin_id}")
            return rdv_id
        except Exception as e:
            logger.error(f"Erreur lors de la création du rendez-vous: {e}")
            conn.rollback()
            raise e
        finally:
            if 'cur' in locals():
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def create_by_user_id(patient_id, user_id, date_heure, statut="En attente", notes=None):
        """Créer un nouveau rendez-vous via user_id"""
        # D'abord, récupérer l'ID du médecin
        medecin_id = Rendezvous._get_medecin_id_from_user_id(user_id)
        if not medecin_id:
            raise Exception("Médecin non trouvé")
        
        # Utiliser la méthode existante
        return Rendezvous.create(patient_id, medecin_id, date_heure, statut, notes)

    @staticmethod
    def update(rdv_id, medecin_id, **kwargs):
        """Mettre à jour un rendez-vous"""
        conn = create_connection()
        if not conn:
            logger.error("Échec de connexion à la base de données")
            return False
        
        try:
            cur = conn.cursor()
            
            # Vérifier que le rendez-vous existe et appartient au médecin
            cur.execute("SELECT id FROM rendezvous WHERE id = %s AND medecin_id = %s", (rdv_id, medecin_id))
            if not cur.fetchone():
                logger.warning(f"Rendez-vous {rdv_id} non trouvé pour le médecin {medecin_id}")
                return False
            
            # Formater la date si présente
            if 'date_heure' in kwargs:
                date_heure = kwargs['date_heure']
                if 'T' in date_heure:
                    date_heure = date_heure.replace('T', ' ')
                if date_heure.endswith('Z'):
                    date_heure = date_heure[:-1]
                kwargs['date_heure'] = date_heure
                
                # Vérifier que la nouvelle date n'est pas déjà prise
                check_query = """
                    SELECT id FROM rendezvous 
                    WHERE medecin_id = %s AND date_heure = %s AND id != %s
                """
                cur.execute(check_query, (medecin_id, date_heure, rdv_id))
                if cur.fetchone():
                    raise Exception("Ce créneau est déjà réservé pour ce médecin")
            
            # Construire la requête de mise à jour
            allowed_fields = ['date_heure', 'statut', 'notes', 'patient_id']
            updates = []
            values = []
            
            for field in allowed_fields:
                if field in kwargs:
                    updates.append(f"{field} = %s")
                    values.append(kwargs[field])
            
            if not updates:
                logger.warning("Aucun champ à mettre à jour")
                return False
            
            # Ajouter les conditions WHERE
            values.append(rdv_id)
            values.append(medecin_id)
            
            query = f"UPDATE rendezvous SET {', '.join(updates)} WHERE id = %s AND medecin_id = %s"
            cur.execute(query, values)
            conn.commit()
            
            success = cur.rowcount > 0
            if success:
                logger.info(f"Rendez-vous {rdv_id} mis à jour pour le médecin {medecin_id}")
            else:
                logger.warning(f"Aucune mise à jour pour le rendez-vous {rdv_id}")
            
            return success
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du rendez-vous: {e}")
            conn.rollback()
            raise e
        finally:
            if 'cur' in locals():
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def update_by_user_id(rdv_id, user_id, **kwargs):
        """Mettre à jour un rendez-vous via user_id"""
        # D'abord, récupérer l'ID du médecin
        medecin_id = Rendezvous._get_medecin_id_from_user_id(user_id)
        if not medecin_id:
            raise Exception("Médecin non trouvé")
        
        # Utiliser la méthode existante
        return Rendezvous.update(rdv_id, medecin_id, **kwargs)

    @staticmethod
    def delete(rdv_id, medecin_id):
        """Supprimer un rendez-vous"""
        conn = create_connection()
        if not conn:
            logger.error("Échec de connexion à la base de données")
            return False
        
        try:
            cur = conn.cursor()
            
            # Vérifier que le rendez-vous existe et appartient au médecin
            cur.execute("SELECT id FROM rendezvous WHERE id = %s AND medecin_id = %s", (rdv_id, medecin_id))
            if not cur.fetchone():
                logger.warning(f"Rendez-vous {rdv_id} non trouvé pour le médecin {medecin_id}")
                return False
            
            query = "DELETE FROM rendezvous WHERE id = %s AND medecin_id = %s"
            cur.execute(query, (rdv_id, medecin_id))
            conn.commit()
            
            success = cur.rowcount > 0
            if success:
                logger.info(f"Rendez-vous {rdv_id} supprimé pour le médecin {medecin_id}")
            else:
                logger.warning(f"Échec de la suppression du rendez-vous {rdv_id}")
            
            return success
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du rendez-vous: {e}")
            conn.rollback()
            return False
        finally:
            if 'cur' in locals():
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def delete_by_user_id(rdv_id, user_id):
        """Supprimer un rendez-vous via user_id"""
        # D'abord, récupérer l'ID du médecin
        medecin_id = Rendezvous._get_medecin_id_from_user_id(user_id)
        if not medecin_id:
            raise Exception("Médecin non trouvé")
        
        # Utiliser la méthode existante
        return Rendezvous.delete(rdv_id, medecin_id)

    @staticmethod
    def check_disponibilite(medecin_id, date_heure):
        """Vérifier si un créneau est disponible pour un médecin"""
        conn = create_connection()
        if not conn:
            return False
        
        try:
            # Formater la date si nécessaire
            if 'T' in date_heure:
                date_heure = date_heure.replace('T', ' ')
            if date_heure.endswith('Z'):
                date_heure = date_heure[:-1]
            
            cur = conn.cursor(dictionary=True)
            query = "SELECT id FROM rendezvous WHERE medecin_id = %s AND date_heure = %s"
            cur.execute(query, (medecin_id, date_heure))
            existing = cur.fetchone()
            
            return existing is None  # True si disponible, False si déjà pris
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de disponibilité: {e}")
            return False
        finally:
            if 'cur' in locals():
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def check_disponibilite_by_user_id(user_id, date_heure):
        """Vérifier la disponibilité via user_id"""
        medecin_id = Rendezvous._get_medecin_id_from_user_id(user_id)
        if not medecin_id:
            return False
        
        return Rendezvous.check_disponibilite(medecin_id, date_heure)

    @staticmethod
    def get_stats(medecin_id):
        """Récupérer les statistiques des rendez-vous pour un médecin"""
        conn = create_connection()
        if not conn:
            return {}
        
        try:
            cur = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    statut,
                    COUNT(*) as count
                FROM rendezvous
                WHERE medecin_id = %s
                GROUP BY statut
            """
            cur.execute(query, (medecin_id,))
            rows = cur.fetchall()
            
            stats = {row['statut']: row['count'] for row in rows}
            total = sum(stats.values())
            
            return {
                'total': total,
                'par_statut': stats
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {}
        finally:
            if 'cur' in locals():
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def get_stats_by_user_id(user_id):
        """Récupérer les statistiques via user_id"""
        medecin_id = Rendezvous._get_medecin_id_from_user_id(user_id)
        if not medecin_id:
            return {}
        
        return Rendezvous.get_stats(medecin_id)

    @staticmethod
    def get_all_future_by_medecin(medecin_id):
        """Récupérer tous les rendez-vous futurs d'un médecin"""
        conn = create_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    r.*,
                    p.nom as patient_nom,
                    p.prenom as patient_prenom,
                    p.telephone as patient_telephone,
                    p.email as patient_email
                FROM rendezvous r
                LEFT JOIN patients p ON r.patient_id = p.id
                WHERE r.medecin_id = %s
                AND r.date_heure >= CURDATE()
                ORDER BY r.date_heure ASC
            """
            cur.execute(query, (medecin_id,))
            rows = cur.fetchall()
            
            rdvs = []
            for row in rows:
                rdv = Rendezvous(
                    id=row['id'],
                    date_heure=row['date_heure'],
                    patient_id=row['patient_id'],
                    medecin_id=row['medecin_id'],
                    statut=row['statut'],
                    notes=row.get('notes'),
                    patient_nom=row.get('patient_nom'),
                    patient_prenom=row.get('patient_prenom'),
                    patient_telephone=row.get('patient_telephone'),
                    patient_email=row.get('patient_email')
                )
                rdvs.append(rdv)
            
            return rdvs
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des RDV futurs: {e}")
            return []
        finally:
            if 'cur' in locals():
                cur.close()
            if conn:
                conn.close()

    def __repr__(self):
        return f'<Rendezvous {self.id} - Patient:{self.patient_id} - Médecin:{self.medecin_id} - {self.date_heure}>'