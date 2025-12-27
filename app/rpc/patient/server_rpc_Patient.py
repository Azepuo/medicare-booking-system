import xmlrpc.server
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta, time, date
import calendar
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
# Fonction pour obtenir une connexion à la base de données
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='medicare_unified',
            user='root',
            password=''
        )
        return conn
    except Error as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

class ServerRPC:
    def __init__(self):
        self.server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 9000), allow_none=True)
        self.server.register_instance(self)

    # ==========================================
    # MÉTHODE: save_patient_review
    # ==========================================
    def save_patient_review(self, user_id, medecin_id, appointment_id, rating, comment):
        """
        Enregistre un avis patient pour un médecin
        Args:
            user_id: ID du patient (depuis JWT validé dans Flask)
            medecin_id: ID du médecin
            appointment_id: ID du rendez-vous
            rating: Note de 1 à 5
            comment: Commentaire du patient
        Returns:
            dict: {"success": True/False, "message": "..."}
        """
        patient_id = user_id
        try:
            print("="*50)
            print(f"[RPC] save_patient_review appelée:")
            print(f"  - Patient: {patient_id}")
            print(f"  - Médecin: {medecin_id}")
            print(f"  - RDV: {appointment_id}")
            print(f"  - Note: {rating}")
            print(f"  - Commentaire: {comment[:50]}...")

            # Validation des données
            if not all([patient_id, medecin_id, appointment_id, rating]):
                return {
                    "success": False,
                    "message": "Tous les champs obligatoires doivent être renseignés"
                }

            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    return {
                        "success": False,
                        "message": "La note doit être entre 1 et 5"
                    }
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "message": "Note invalide"
                }

            # Valider le commentaire
            if not comment or len(comment.strip()) < 10:
                return {
                    "success": False,
                    "message": "Le commentaire doit contenir au moins 10 caractères"
                }

            if len(comment) > 500:
                return {
                    "success": False,
                    "message": "Le commentaire ne peut pas dépasser 500 caractères"
                }

            conn = get_db_connection()
            cursor = conn.cursor()

            # 1. Vérifier que le rendez-vous existe et appartient au patient
            cursor.execute("""
                SELECT r.id, r.statut, r.medecin_id, r.patient_id
                FROM rendezvous r
                WHERE r.id = %s AND r.patient_id = %s
            """, (appointment_id, patient_id))

            rdv = cursor.fetchone()

            if not rdv:
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "message": "Rendez-vous introuvable ou non autorisé"
                }

            # Vérifier que le médecin correspond
            if rdv[2] != int(medecin_id):
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "message": "Le médecin ne correspond pas au rendez-vous"
                }

            # 2. Vérifier que le RDV est terminé
            if rdv[1].lower() != 'terminé':
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "message": "Vous ne pouvez donner un avis que pour un rendez-vous terminé"
                }

            # 3. Vérifier si un avis existe déjà pour ce RDV
            cursor.execute("""
                SELECT id FROM avis
                WHERE patient_id = %s 
                  AND medecin_id = %s 
                  AND rendezvous_id = %s
            """, (patient_id, medecin_id, appointment_id))

            existing_avis = cursor.fetchone()

            if existing_avis:
                # Mise à jour de l'avis existant
                cursor.execute("""
                    UPDATE avis
                    SET note = %s, 
                        commentaire = %s, 
                        date_avis = NOW()
                    WHERE id = %s
                """, (rating, comment.strip(), existing_avis[0]))
                
                conn.commit()
                message = "Votre avis a été mis à jour avec succès"
                print(f"[RPC] ✅ Avis {existing_avis[0]} mis à jour")
            else:
                # Insertion d'un nouvel avis
                cursor.execute("""
                    INSERT INTO avis (
                        patient_id, 
                        medecin_id, 
                        note, 
                        commentaire, 
                        date_avis,
                        rendezvous_id
                    )
                    VALUES (%s, %s, %s, %s, NOW(), %s)
                """, (patient_id, medecin_id, rating, comment.strip(), appointment_id))
                
                conn.commit()
                message = "Votre avis a été enregistré avec succès"
                print(f"[RPC] ✅ Nouvel avis créé")

            cursor.close()
            conn.close()
            print(f"[RPC] ✅ Avis enregistré avec succès")
            print("="*50)

            return {
                "success": True,
                "message": message
            }

        except Exception as e:
            print(f"[RPC] ❌ Erreur inattendue: {e}")
            import traceback
            traceback.print_exc()
            try:
                conn.rollback()
                cursor.close()
                conn.close()
            except:
                pass
            return {
                "success": False,
                "message": f"Erreur lors de l'enregistrement: {str(e)}"
            }

    # ==========================================
    # MÉTHODE: get_patient_info
    # ==========================================
    def get_patient_info(self, user_id):
        """
        Récupère les informations basiques du patient
        """
        patient_id = user_id
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT nom, email
                FROM patients
                WHERE user_id = %s
            """, (patient_id,))
            patient_info = cursor.fetchone()
            if patient_info is None:
                print(f"[DEBUG] ⚠️ Aucun patient trouvé avec user_id={patient_id}")
                return {"success": False, "message": "Patient introuvable"}
            print(f"[DEBUG] ✅ Patient trouvé: {patient_info}")
            cursor.close()
            conn.close()
            return patient_info
        except Error as e:
            print(f"[DEBUG] ❌ Erreur SQL: {e}")
            return {"success": False, "message": str(e)}
        except Exception as e:
            print(f"[DEBUG] ❌ Erreur inattendue: {e}")
            return {"success": False, "message": str(e)}

    # ==========================================
    # MÉTHODE: get_dashboard
    # ==========================================
    def get_dashboard(self, user_id):
        """
        Récupère les données du dashboard patient
        """
        patient_id = user_id
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Récupérer les infos du patient
            cursor.execute("SELECT nom, email FROM patients WHERE user_id=%s", (patient_id,))
            patient_info = cursor.fetchone()
            if patient_info is None:
                patient_info = {"nom": "", "email": ""} 
            
            # Récupérer l'ID interne du patient
            cursor.execute("SELECT id FROM patients WHERE user_id=%s", (patient_id,))
            patient_row = cursor.fetchone()
            if not patient_row:
                return {
                    "patient_info": patient_info,
                    "upcoming_appointments": [],
                    "past_appointments": []
                }
            
            internal_patient_id = patient_row['id']
            
            # Récupérer les prochains rendez-vous
            cursor.execute("""
                SELECT r.id, r.date_heure, r.statut, r.notes,
                    m.nom AS medecin_nom, 
                    m.photo_url,
                    s.nom AS specialite
                FROM rendezvous r
                JOIN medecins m ON r.medecin_id = m.id
                JOIN specialisations s ON m.id_specialisation=s.id
                WHERE r.patient_id=%s AND r.date_heure >= NOW() AND r.statut NOT IN ('Annulé', 'En attente', 'terminé')
                ORDER BY r.date_heure ASC
            """, (internal_patient_id,))
            upcoming_appointments = cursor.fetchall()
            print(f"[RPC] Rendez-vous à venir bruts: {upcoming_appointments}")
            
            # Formater les dates
            for appointment in upcoming_appointments:
                if isinstance(appointment["date_heure"], datetime):
                    appointment["date_heure"] = appointment["date_heure"].strftime("%Y-%m-%d %H:%M")
                else:
                    print(f"[RPC] Attention, date_heure n'est pas un datetime: {appointment['date_heure']}")

            # Récupérer l'historique des 3 derniers rendez-vous
            cursor.execute("""
                SELECT r.date_heure, m.nom AS medecin_nom, r.statut
                FROM rendezvous r
                JOIN medecins m ON r.medecin_id = m.id
                WHERE r.patient_id=%s
                ORDER BY r.date_heure DESC
                LIMIT 3
            """, (internal_patient_id,))
            past_appointments = cursor.fetchall()
            print(f"[RPC] Rendez-vous passés bruts: {past_appointments}")
            
            # Formater les dates
            for appointment in past_appointments:
                if isinstance(appointment["date_heure"], datetime):
                    appointment["date_heure"] = appointment["date_heure"].strftime("%Y-%m-%d %H:%M")
                else:
                    print(f"[RPC] Attention, date_heure n'est pas un datetime: {appointment['date_heure']}")

            cursor.close()
            conn.close()

            result = {
                "patient_info": patient_info,
                "upcoming_appointments": upcoming_appointments,
                "past_appointments": past_appointments
            }
            print(f"[RPC] Résultat final renvoyé: {result}")
            return result
        except Error as e:
            print(f"[RPC] Erreur dans get_dashboard: {e}")
            return {"success": False, "message": str(e)}

    # ==========================================
    # MÉTHODE: get_all_appointments
    # ==========================================
    def get_all_appointments(self, user_id):
        """
        Récupère tous les rendez-vous du patient
        """
        patient_id = user_id
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Récupérer l'ID interne du patient
            cursor.execute("SELECT id FROM patients WHERE user_id=%s", (patient_id,))
            patient_row = cursor.fetchone()
            if not patient_row:
                return []
            
            internal_patient_id = patient_row['id']
            
            cursor.execute("""
                SELECT 
                    r.id, 
                    r.date_heure, 
                    r.statut,  
                    m.clinic,
                    r.notes,
                    m.user_id as medecin_id,
                    m.nom AS medecin_nom, 
                    s.nom AS specialite,
                    DATE(r.date_heure) as date_only,
                    TIME_FORMAT(r.date_heure, '%H:%i') as time_only
                FROM rendezvous r
                JOIN medecins m ON r.medecin_id = m.id
                JOIN specialisations s ON m.id_specialisation = s.id
                WHERE r.patient_id = %s
                ORDER BY r.date_heure DESC
            """, (internal_patient_id,))
            all_appointments = cursor.fetchall()
            cursor.close()
            conn.close()

            # Formater les heures sans les secondes
            for appointment in all_appointments:
                if isinstance(appointment["date_heure"], (datetime, date)):
                    appointment["date_heure"] = appointment["date_heure"].strftime("%Y-%m-%d %H:%M")
                
                if isinstance(appointment.get("date_heure"), str):
                    try:
                        dt = datetime.strptime(appointment["date_heure"], "%Y-%m-%d %H:%M")
                        appointment["date_only"] = dt.strftime("%Y-%m-%d")
                        appointment["time_only"] = dt.strftime("%H:%M")
                    except:
                        appointment["date_only"] = appointment["date_heure"][:10] if len(appointment["date_heure"]) >= 10 else ""
                        appointment["time_only"] = appointment["date_heure"][11:16] if len(appointment["date_heure"]) >= 16 else ""
                elif isinstance(appointment.get("date_heure"), datetime):
                    appointment["date_only"] = appointment["date_heure"].strftime("%Y-%m-%d")
                    appointment["time_only"] = appointment["date_heure"].strftime("%H:%M")
                
                for key in appointment.keys():
                    if appointment[key] is None:
                        appointment[key] = ""
                    elif isinstance(appointment[key], (date, datetime)):
                        appointment[key] = appointment[key].strftime("%Y-%m-%d")
            
            print(f"[RPC] get_all_appointments retourne {len(all_appointments)} RDV")
            if all_appointments and len(all_appointments) > 0:
                print(f"[RPC] Exemple de RDV formaté: {all_appointments[0]}")
            
            return all_appointments
    
        except Error as e:
            print(f"[RPC] Erreur dans get_all_appointments: {e}")
            return {"success": False, "message": str(e)}

    # ==========================================
    # MÉTHODE: update_appointment
    # ==========================================
    def update_appointment(self, user_id, appointment_id, medecin_id, date, time_str, notes):
        """
        Met à jour un rendez-vous existant
        """
        patient_id = user_id
        
        try:
            if not (appointment_id and medecin_id and date and time_str):
                return {"success": False, "message": "Tous les champs sont requis."}

            date_heure_str = f"{date} {time_str}:00"

            conn = get_db_connection()
            cursor = conn.cursor()

            # Récupérer l'ID interne du patient
            cursor.execute("SELECT id FROM patients WHERE user_id=%s", (patient_id,))
            patient_row = cursor.fetchone()
            if not patient_row:
                cursor.close()
                conn.close()
                return {"success": False, "message": "Patient introuvable"}
            
            internal_patient_id = patient_row[0]
            
            # Récupérer l'ID interne du médecin
            cursor.execute("SELECT id FROM medecins WHERE user_id=%s", (medecin_id,))
            medecin_row = cursor.fetchone()
            if not medecin_row:
                cursor.close()
                conn.close()
                return {"success": False, "message": "Médecin introuvable"}
            
            internal_medecin_id = medecin_row[0]

            # Vérifier que le RDV appartient au patient connecté
            cursor.execute("""
                SELECT patient_id 
                FROM rendezvous 
                WHERE id = %s
            """, (appointment_id,))
            
            rdv = cursor.fetchone()
            
            if not rdv:
                cursor.close()
                conn.close()
                return {
                    "success": False, 
                    "message": "Rendez-vous introuvable"
                }
            
            if rdv[0] != internal_patient_id:
                cursor.close()
                conn.close()
                print(f"[SECURITY] ⚠️ Patient {patient_id} a tenté de modifier le RDV {appointment_id} du patient {rdv[0]}")
                return {
                    "success": False, 
                    "message": "Vous n'êtes pas autorisé à modifier ce rendez-vous"
                }

            # Vérification si le patient a déjà un rendez-vous pour ce médecin et cette date
            cursor.execute("""
                SELECT COUNT(*) 
                FROM rendezvous
                WHERE patient_id = %s 
                  AND medecin_id = %s 
                  AND DATE(date_heure) = %s
                  AND statut != 'Annulé'
                  AND id != %s
            """, (internal_patient_id, internal_medecin_id, date, appointment_id))

            already_has = cursor.fetchone()[0]
            if already_has > 0:
                cursor.close()
                conn.close()
                return {
                    "success": False, 
                    "message": "Vous avez déjà un rendez-vous ce jour-là avec ce médecin."
                }

            # Vérification du conflit de créneaux horaires
            cursor.execute("""
                SELECT COUNT(*) 
                FROM rendezvous
                WHERE medecin_id = %s 
                  AND date_heure = %s
                  AND id != %s
                  AND statut != 'Annulé'
            """, (internal_medecin_id, date_heure_str, appointment_id))
            conflict = cursor.fetchone()[0]

            if conflict > 0:
                cursor.close()
                conn.close()
                return {
                    "success": False, 
                    "message": "Ce créneau est déjà pris par un autre patient."
                }

            # Mise à jour sécurisée
            cursor.execute("""
                UPDATE rendezvous
                SET medecin_id = %s, date_heure = %s, notes = %s, statut = "En attente"
                WHERE id = %s AND patient_id = %s
            """, (internal_medecin_id, date_heure_str, notes, appointment_id, internal_patient_id))

            conn.commit()
            cursor.close()
            conn.close()

            print(f"[RPC] ✅ RDV {appointment_id} mis à jour par patient {patient_id}")
            return {"success": True}
            
        except Error as e:
            print(f"[RPC] ❌ Erreur update_appointment: {e}")
            return {"success": False, "message": str(e)}

    # ==========================================
    # MÉTHODE: cancel_appointment
    # ==========================================
    def cancel_appointment(self, user_id, appointment_id):
        """
        Annule un rendez-vous existant
        """
        patient_id = user_id
        
        try:
            if not appointment_id:
                return {"success": False, "message": "ID du rendez-vous manquant"}

            conn = get_db_connection()
            cursor = conn.cursor()

            # Récupérer l'ID interne du patient
            cursor.execute("SELECT id FROM patients WHERE user_id=%s", (patient_id,))
            patient_row = cursor.fetchone()
            if not patient_row:
                cursor.close()
                conn.close()
                return {"success": False, "message": "Patient introuvable"}
            
            internal_patient_id = patient_row[0]

            # Vérifier que le RDV appartient bien au patient connecté
            cursor.execute("""
                SELECT patient_id 
                FROM rendezvous 
                WHERE id = %s
            """, (appointment_id,))
            
            rdv = cursor.fetchone()
            
            if not rdv:
                cursor.close()
                conn.close()
                return {
                    "success": False, 
                    "message": "Rendez-vous introuvable"
                }
            
            if rdv[0] != internal_patient_id:
                cursor.close()
                conn.close()
                print(f"[SECURITY] ⚠️ Patient {patient_id} a tenté d'annuler le RDV {appointment_id} du patient {rdv[0]}")
                return {
                    "success": False, 
                    "message": "Vous n'êtes pas autorisé à annuler ce rendez-vous"
                }

            # Annuler le rendez-vous
            cursor.execute("""
                UPDATE rendezvous 
                SET statut = 'Annulé' 
                WHERE id = %s AND patient_id = %s
            """, (appointment_id, internal_patient_id))

            conn.commit()
            cursor.close()
            conn.close()

            print(f"[RPC] ✅ RDV {appointment_id} annulé par patient {patient_id}")
            return {"success": True, "message": "Rendez-vous annulé avec succès"}
            
        except Error as e:
            print(f"[RPC] ❌ Erreur cancel_appointment: {e}")
            return {"success": False, "message": str(e)}

    # ==========================================
    # MÉTHODE: get_profile_local
    # ==========================================
    def get_profile_local(self, user_id):
        """
        Récupère le profil complet du patient
        """
        patient_id = user_id
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT id, nom, email, telephone FROM patients WHERE user_id=%s", (patient_id,))
            patient_info = cursor.fetchone()

            if not patient_info:
                cursor.close()
                conn.close()
                return {"success": False, "message": "Patient introuvable"}

            internal_patient_id = patient_info['id']
            
            cursor.execute("SELECT COUNT(*) as rdv_count FROM rendezvous WHERE patient_id=%s", (internal_patient_id,))
            rdv_count = cursor.fetchone()

            cursor.close()
            conn.close()

            return {
                "patient_info": patient_info,
                "total_rdv": rdv_count["rdv_count"]
            }
        except Error as e:
            return {"success": False, "message": str(e)}

    # ==========================================
    # MÉTHODE: update_profile
    # ==========================================
    def update_profile(self, user_id, nom, email, telephone):
        """
        Met à jour les informations du profil patient
        """
        patient_id = user_id
        try:
            if not nom or not email or not telephone:
                return {"success": False, "message": "Tous les champs sont obligatoires"}

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE patients
                SET nom = %s, email = %s, telephone = %s
                WHERE user_id = %s
            """, (nom, email, telephone, patient_id))
            conn.commit()
            cursor.close()
            conn.close()

            return {"success": True, "message": "Profil mis à jour avec succès"}
        except Error as e:
            return {"success": False, "message": str(e)}

    # ==========================================
    # MÉTHODE: logout
    # ==========================================
    def logout(self):
        """
        Gère la déconnexion (méthode simple)
        """
        return {"success": True, "message": "Déconnexion réussie"}

    # ==========================================
    # MÉTHODE: get_doctors_local
    # ==========================================
    def get_doctors_local(self, specialization_id):
        """
        Récupère les médecins par spécialisation
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT user_id as id, nom 
                FROM medecins
                WHERE id_specialisation = %s
            """, (specialization_id,))
            doctors = cursor.fetchall()
            cursor.close()
            conn.close()
            return doctors
        except Error as e:
            return {"success": False, "message": str(e)}

    # ==========================================
    # MÉTHODE: get_available_slots_local
    # ==========================================
    def get_available_slots_local(self, doctor_id, consultation_date):
        """
        Récupère les créneaux horaires disponibles pour un médecin
        """
        try:
            print(f"[RPC] get_available_slots_local pour médecin {doctor_id} le {consultation_date}")

            jours_en_fr = {
                "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
                "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi",
                "Sunday": "Dimanche"
            }

            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Récupérer l'ID interne du médecin
            cursor.execute("SELECT id FROM medecins WHERE user_id=%s", (doctor_id,))
            medecin_row = cursor.fetchone()
            if not medecin_row:
                cursor.close()
                conn.close()
                return {"success": False, "slots": []}
            
            internal_medecin_id = medecin_row[0]

            date_obj = datetime.strptime(consultation_date, "%Y-%m-%d")
            jour_semaine = jours_en_fr[date_obj.strftime("%A")]

            # Récupérer les disponibilités
            cursor.execute("""
                SELECT heure_debut, heure_fin
                FROM disponibilites
                WHERE medecin_id=%s AND jour_semaine=%s
            """, (internal_medecin_id, jour_semaine))

            dispo_list = cursor.fetchall()
            slots = []

            for dispo in dispo_list:
                # Convertir les heures
                if isinstance(dispo[0], timedelta):
                    start_time = (datetime.min + dispo[0]).time()
                else:
                    start_time = datetime.strptime(str(dispo[0]), "%H:%M:%S").time()
                
                if isinstance(dispo[1], timedelta):
                    end_time = (datetime.min + dispo[1]).time()
                else:
                    end_time = datetime.strptime(str(dispo[1]), "%H:%M:%S").time()

                current_time = datetime.combine(date_obj, start_time)
                end_datetime = datetime.combine(date_obj, end_time)

                while current_time < end_datetime:
                    slot_start_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    slot_end_time = current_time + timedelta(minutes=30)
                    slot_end_str = slot_end_time.strftime("%Y-%m-%d %H:%M:%S")

                    # Vérifier les conflits
                    cursor.execute("""
                        SELECT COUNT(*) FROM rendezvous
                        WHERE medecin_id=%s AND date_heure >= %s AND date_heure < %s
                    """, (internal_medecin_id, slot_start_str, slot_end_str))
                    conflict = cursor.fetchone()[0]

                    if conflict == 0:
                        slot_display = current_time.strftime("%H:%M")
                        slots.append(slot_display)

                    current_time += timedelta(minutes=30)

            cursor.close()
            conn.close()
            
            print(f"[RPC] ✅ {len(slots)} créneaux disponibles")
            
            return {"success": True, "slots": slots}
            
        except Exception as e:
            print(f"[RPC] ❌ Erreur get_available_slots_local: {e}")
            return {"success": False, "slots": []}

    # ==========================================
    # MÉTHODE: book_appointment
    # ==========================================
    def book_appointment(self, user_id, doctor_id, consultation_date, consultation_time, reason=""):
        """
        Réserve un rendez-vous
        """
        patient_id = user_id
        try:
            print(f"[RPC] book_appointment pour patient {patient_id}")

            # Validation des champs
            if not all([patient_id, doctor_id, consultation_date, consultation_time]):
                return {
                    "success": False,
                    "message": "Tous les champs sont requis."
                }

            print(f"[RPC] Date: '{consultation_date}', Heure: '{consultation_time}'")
        
            # Combiner date et heure
            if ":" in consultation_time and consultation_time.count(":") == 1:
                consultation_time = consultation_time + ":00"
        
            date_heure_str = f"{consultation_date} {consultation_time}"
            print(f"[RPC] Date/heure combinée: '{date_heure_str}'")
        
            # Parser la date/heure
            try:
                formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"]
                date_heure = None
                
                for fmt in formats:
                    try:
                        date_heure = datetime.strptime(date_heure_str, fmt)
                        print(f"[RPC] Date parsée: {date_heure}")
                        break
                    except ValueError:
                        continue
                
                if date_heure is None:
                    return {
                        "success": False,
                        "message": f"Format de date invalide: '{date_heure_str}'"
                    }
                
            except Exception as parse_error:
                print(f"[RPC] Erreur parsing: {parse_error}")
                return {
                    "success": False,
                    "message": f"Erreur de format de date: {str(parse_error)}"
                }

            # Vérifier que la date n'est pas dans le passé
            if date_heure < datetime.now():
                return {
                    "success": False,
                    "message": "Impossible de prendre un rendez-vous dans le passé."
                }

            # Connexion à la DB
            conn = get_db_connection()
            cursor = conn.cursor()

            # Récupérer l'ID interne du patient
            cursor.execute("SELECT id FROM patients WHERE user_id=%s", (patient_id,))
            patient_row = cursor.fetchone()
            if not patient_row:
                cursor.close()
                conn.close()
                return {"success": False, "message": "Patient introuvable"}
            
            internal_patient_id = patient_row[0]

            # Vérifier si le médecin existe et récupérer son ID interne
            cursor.execute("SELECT id, nom FROM medecins WHERE user_id = %s", (doctor_id,))
            medecin = cursor.fetchone()
            if not medecin:
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "message": "Médecin non trouvé."
                }
            
            internal_medecin_id = medecin[0]
            print(f"[RPC] Médecin trouvé: {medecin[1]}")

            # Vérifier conflit de rendez-vous (créneau déjà pris)
            db_date_heure_str = date_heure.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[RPC] Vérification conflit pour: {db_date_heure_str}")
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM rendezvous
                WHERE medecin_id = %s 
                  AND date_heure = %s
                  AND statut != 'Annulé'
            """, (internal_medecin_id, db_date_heure_str))
            
            conflict = cursor.fetchone()[0]
            print(f"[RPC] Conflits trouvés: {conflict}")

            if conflict > 0:
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "message": "Ce créneau est déjà pris par un autre patient."
                }

            # Vérifier si le patient a déjà un RDV ce jour avec ce médecin
            cursor.execute("""
                SELECT COUNT(*) 
                FROM rendezvous
                WHERE patient_id = %s 
                  AND medecin_id = %s 
                  AND DATE(date_heure) = DATE(%s)
                  AND statut != 'Annulé'
            """, (internal_patient_id, internal_medecin_id, db_date_heure_str))

            already_has = cursor.fetchone()[0]
            print(f"[RPC] RDV existants ce jour: {already_has}")

            if already_has > 0:
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "message": "Vous avez déjà un rendez-vous ce jour-là avec ce médecin."
                }

            # Insérer le rendez-vous
            cursor.execute("""
                INSERT INTO rendezvous (date_heure, patient_id, medecin_id, statut, notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (db_date_heure_str, internal_patient_id, internal_medecin_id, "En attente", reason))
            
            rdv_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"[RPC] ✅ RDV {rdv_id} créé avec succès")
            return {
                "success": True,
                "message": "Rendez-vous pris avec succès!",
                "appointment_id": rdv_id
            }
            
        except Exception as e:
            print(f"[RPC] ❌ Erreur book_appointment: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                conn.rollback()
                cursor.close()
                conn.close()
            except:
                pass
                
            return {
                "success": False,
                "message": f"Erreur lors de la prise de rendez-vous: {str(e)}"
            }

    # ==========================================
    # MÉTHODE: get_honoraires_local
    # ==========================================
    def get_honoraires_local(self, doctor_id):
        """
        Récupère les honoraires d'un médecin
        """
        try:
            print(f"[RPC] get_honoraires_local pour médecin {doctor_id}")

            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, tarif_consultation 
                FROM medecins
                WHERE user_id = %s
            """, (doctor_id,))
            
            medecin = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if medecin:
                tarif = float(medecin[1]) if medecin[1] is not None else 0.0
                print(f"[RPC] ✅ Honoraire trouvé: {medecin[1]}")
                return [{"id": medecin[0], "montant": tarif}]
            else:
                print(f"[RPC] ⚠️ Médecin non trouvé")
                return []
            
        except Exception as e:
            print(f"[RPC] ❌ Erreur get_honoraires_local: {e}")
            return []

    # ==========================================
    # MÉTHODE: get_available_dates_local
    # ==========================================
    def get_available_dates_local(self, doctor_id):
        """
        Récupère les dates disponibles pour un médecin
        """
        try:
            print(f"[RPC] get_available_dates_local pour médecin {doctor_id}")

            jours_en_fr = {
                "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
                "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi",
                "Sunday": "Dimanche"
            }

            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Récupérer l'ID interne du médecin
            cursor.execute("SELECT id FROM medecins WHERE user_id=%s", (doctor_id,))
            medecin_row = cursor.fetchone()
            if not medecin_row:
                cursor.close()
                conn.close()
                return {"success": False, "dates": []}
            
            internal_medecin_id = medecin_row[0]

            today = datetime.today().date()
            available_dates = []
            
            # Chercher sur les 3 prochains mois
            for month_offset in range(0, 3):
                year = today.year
                month = today.month + month_offset
                
                if month > 12:
                    year += 1
                    month -= 12
                
                _, nb_jours = calendar.monthrange(year, month)

                for day in range(1, nb_jours + 1):
                    date_obj = datetime(year, month, day).date()
                    
                    if date_obj < today:
                        continue
                    
                    jour_semaine = jours_en_fr[date_obj.strftime("%A")]
                    date_str = date_obj.strftime("%Y-%m-%d")

                    # Vérifier les disponibilités
                    cursor.execute("""
                        SELECT heure_debut, heure_fin
                        FROM disponibilites
                        WHERE medecin_id=%s AND jour_semaine=%s
                    """, (internal_medecin_id, jour_semaine))
                    dispo_list = cursor.fetchall()

                    day_has_slot = False

                    for dispo in dispo_list:
                        start_time = (datetime.min + dispo[0]).time() if isinstance(dispo[0], timedelta) else dispo[0]
                        end_time = (datetime.min + dispo[1]).time() if isinstance(dispo[1], timedelta) else dispo[1]

                        if not isinstance(start_time, time) or not isinstance(end_time, time):
                            continue

                        current_time = datetime.combine(date_obj, start_time)
                        end_datetime = datetime.combine(date_obj, end_time)

                        while current_time <= end_datetime:
                            slot_start = current_time.strftime("%Y-%m-%d %H:%M:%S")
                            slot_end_dt = current_time + timedelta(minutes=30)
                            slot_end = slot_end_dt.strftime("%Y-%m-%d %H:%M:%S")

                            cursor.execute("""
                                SELECT COUNT(*) FROM rendezvous
                                WHERE medecin_id=%s AND date_heure >= %s AND date_heure < %s
                            """, (internal_medecin_id, slot_start, slot_end))
                            conflict = cursor.fetchone()[0]

                            if conflict == 0:
                                day_has_slot = True
                                break

                            current_time += timedelta(minutes=30)

                        if day_has_slot:
                            break

                    if day_has_slot:
                        available_dates.append(date_str)

            cursor.close()
            conn.close()
            
            print(f"[RPC] ✅ {len(available_dates)} dates disponibles")
            
            return {"success": bool(available_dates), "dates": sorted(list(set(available_dates)))}
            
        except Exception as e:
            print(f"[RPC] ❌ Erreur get_available_dates_local: {e}")
            return {"success": False, "dates": []}

    # ==========================================
    # MÉTHODE: get_rendezvous_details
    # ==========================================
    def get_rendezvous_details(self, user_id, rdv_id):
        """
        Récupère les détails complets d'un rendez-vous
        """
        patient_id = user_id
        
        try:
            print(f"[RPC] 🔍 Récupération des détails du rendez-vous {rdv_id} pour patient {patient_id}")
            
            conn = get_db_connection()
            if not conn:
                print("[RPC] ❌ Échec de connexion à la BD")
                return {
                    "success": False,
                    "message": "Erreur de connexion à la base de données"
                }
            
            cursor = conn.cursor(dictionary=True)
            
            # Récupérer l'ID interne du patient
            cursor.execute("SELECT id FROM patients WHERE user_id=%s", (patient_id,))
            patient_row = cursor.fetchone()
            if not patient_row:
                cursor.close()
                conn.close()
                return {"success": False, "message": "Patient introuvable"}
            
            internal_patient_id = patient_row['id']
            
            # Requête avec vérification de propriété
            cursor.execute("""
                SELECT 
                    r.id,
                    r.date_heure,
                    r.statut,
                    r.notes,
                    r.patient_id,
                    m.nom as medecin_nom,
                    m.email as medecin_email,
                    m.telephone as medecin_telephone,
                    m.tarif_consultation,
                    m.photo_url,
                    m.clinic as adresse_cabinet,
                    s.nom as specialite,
                    s.description as specialite_description
                FROM rendezvous r
                JOIN medecins m ON r.medecin_id = m.id
                LEFT JOIN specialisations s ON m.id_specialisation = s.id
                WHERE r.id = %s
            """, (rdv_id,))
            
            rdv = cursor.fetchone()
            
            if not rdv:
                cursor.close()
                conn.close()
                print(f"[RPC] ⚠️ Rendez-vous {rdv_id} introuvable")
                return {
                    "success": False,
                    "message": "Rendez-vous introuvable"
                }
            
            # Vérifier que le RDV appartient au patient connecté
            if rdv["patient_id"] != internal_patient_id:
                cursor.close()
                conn.close()
                print(f"[SECURITY] ⚠️ Patient {patient_id} a tenté d'accéder au RDV {rdv_id} du patient {rdv['patient_id']}")
                return {
                    "success": False,
                    "message": "Vous n'êtes pas autorisé à voir ce rendez-vous"
                }
            
            # Supprimer patient_id avant de renvoyer
            del rdv["patient_id"]
            
            # Formater la date
            if isinstance(rdv.get("date_heure"), datetime):
                rdv["date_heure"] = rdv["date_heure"].strftime("%Y-%m-%d %H:%M")
            
            # Convertir tous les objets date/datetime en strings
            for key, value in rdv.items():
                if isinstance(value, (datetime, date)):
                    rdv[key] = value.strftime(
                        "%Y-%m-%d %H:%M" if isinstance(value, datetime) else "%Y-%m-%d"
                    )
            
            # Convertir Decimal en float et remplacer None
            for key in rdv.keys():
                if rdv[key] is None:
                    rdv[key] = ""
                elif isinstance(rdv[key], Decimal):
                    rdv[key] = float(rdv[key])
            
            print(f"[RPC] ✅ Détails du rendez-vous {rdv_id} récupérés")
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "data": rdv
            }
            
        except mysql.connector.Error as db_error:
            print(f"[RPC] ❌ Erreur SQL: {db_error}")
            import traceback
            traceback.print_exc()
            
            try:
                cursor.close()
                conn.close()
            except:
                pass
            
            return {
                "success": False,
                "message": f"Erreur base de données: {str(db_error)}"
            }
            
        except Exception as e:
            print(f"[RPC] ❌ Erreur inattendue: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                cursor.close()
                conn.close()
            except:
                pass
                
            return {
                "success": False,
                "message": f"Erreur lors de la récupération: {str(e)}"
            }
    # ==========================================
    # MÉTHODE: mark_notification_as_read
    # ==========================================
    def mark_notification_as_read(self, user_id, notification_id):
        """
        Marque une notification comme lue
        """
        patient_id = user_id
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Récupérer l'ID interne du patient
            cursor.execute("SELECT id FROM patients WHERE user_id=%s", (patient_id,))
            patient_row = cursor.fetchone()
            if not patient_row:
                cursor.close()
                conn.close()
                return {"success": False, "message": "Patient introuvable"}
            
            internal_patient_id = patient_row[0]
            
            # Vérifier que la notification appartient au patient
            cursor.execute("""
                SELECT patient_id 
                FROM notifications 
                WHERE id = %s
            """, (notification_id,))
            
            notif = cursor.fetchone()
            
            if not notif:
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "message": "Notification introuvable"
                }
            
            if notif[0] != internal_patient_id:
                cursor.close()
                conn.close()
                print(f"[SECURITY] ⚠️ Patient {patient_id} a tenté de marquer la notification {notification_id}")
                return {
                    "success": False,
                    "message": "Vous n'êtes pas autorisé à modifier cette notification"
                }
            
            # Mettre à jour
            cursor.execute("""
                UPDATE notifications
                SET lue = TRUE, date_lecture = NOW()
                WHERE id = %s AND patient_id = %s
            """, (notification_id, internal_patient_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"[RPC] ✅ Notification {notification_id} marquée comme lue")
            return {"success": True}
            
        except Exception as e:
            print(f"[RPC] ❌ Erreur mark_notification_as_read: {e}")
            try:
                cursor.close()
                conn.close()
            except:
                pass
            return {"success": False, "message": str(e)}
    # ==========================================
    # MÉTHODE: get_unread_count
    # ==========================================
    def get_unread_count(self, user_id):
        """
        Compte les notifications non lues
        """
        patient_id = user_id
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Récupérer l'ID interne du patient
            cursor.execute("SELECT id FROM patients WHERE user_id=%s", (patient_id,))
            patient_row = cursor.fetchone()
            if not patient_row:
                cursor.close()
                conn.close()
                return {"success": False, "count": 0}
            
            internal_patient_id = patient_row[0]
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM notifications
                WHERE patient_id = %s AND lue = FALSE
            """, (internal_patient_id,))
            
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            print(f"[RPC] ✅ Patient {patient_id} a {count} notifications non lues")
            return {"success": True, "count": count}
            
        except Exception as e:
            print(f"[RPC] ❌ Erreur get_unread_count: {e}")
            return {"success": False, "count": 0}
    # ==========================================
    # MÉTHODE: get_notifications
    # ==========================================
    def get_notifications(self, user_id, limit):
        """
        Récupère les dernières notifications d'un patient
        """
        patient_id = user_id
        try:
            print("="*70)
            print(f"[DEBUG] 🚀 Entrée dans get_notifications(patient_id={patient_id}, limit={limit})")

            conn = get_db_connection()
            if conn is None:
                print("[DEBUG] ❌ Connexion DB échouée !")
                return {"success": False, "notifications": []}
            else:
                print("[DEBUG] ✅ Connexion DB établie")

            cursor = conn.cursor(dictionary=True)
            
            # Récupérer l'ID interne du patient
            cursor.execute("SELECT id FROM patients WHERE user_id=%s", (patient_id,))
            patient_row = cursor.fetchone()
            if not patient_row:
                cursor.close()
                conn.close()
                return {"success": False, "notifications": []}
            
            internal_patient_id = patient_row['id']

            # Exécuter la requête SQL
            print("[DEBUG] 🧾 Exécution de la requête SQL...")
            cursor.execute("""
                SELECT 
                    n.id,
                    n.titre,
                    n.message,
                    n.type,
                    n.lue,
                    n.date_creation,
                    n.rendezvous_id
                FROM notifications n
                WHERE n.patient_id = %s
                ORDER BY n.date_creation DESC
                LIMIT %s
            """, (internal_patient_id, limit))

            notifications = cursor.fetchall()
            print(f"[DEBUG] 📦 Résultats bruts récupérés: {len(notifications)} ligne(s)")

            # Si aucune notification
            if not notifications:
                print("[DEBUG] ⚠️ Aucune notification trouvée pour ce patient !")

            # Formater les dates
            for notif in notifications:
                if isinstance(notif.get("date_creation"), datetime):
                    notif["date_creation"] = notif["date_creation"].strftime("%Y-%m-%d %H:%M:%S")

            cursor.close()
            conn.close()
            print("[DEBUG] ✅ Connexion fermée proprement")

            print(f"[DEBUG] ✅ Retour final: {len(notifications)} notifications")
            print("="*70)

            return {"success": True, "notifications": notifications}

        except Exception as e:
            print(f"[DEBUG] ❌ Erreur inattendue dans get_notifications: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "notifications": []}
    # ==========================================
    # MÉTHODE: change_password
    # ==========================================
    def change_password(self, user_id, old_password, new_password):
     """
    Change le mot de passe d'un patient en utilisant bcrypt
    """
     try:
        print("="*50)
        print(f"[RPC] change_password appelée:")
        print(f"  - User ID: {user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Récupérer le mot de passe actuel depuis la table users
        cursor.execute("SELECT password FROM users WHERE id=%s", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            return {"success": False, "message": "Utilisateur introuvable"}

        stored_password = row["password"]
        print(f"[DEBUG] Mot de passe stocké: {stored_password[:60]}...")

        # Vérifier l'ancien mot de passe avec bcrypt
        # Convertir les chaînes en bytes pour bcrypt
        if isinstance(stored_password, str):
            stored_password_bytes = stored_password.encode('utf-8')
        else:
            stored_password_bytes = stored_password
            
        old_password_bytes = old_password.encode('utf-8')
        
        if not bcrypt.checkpw(old_password_bytes, stored_password_bytes):
            print(f"[DEBUG] ❌ Mot de passe incorrect")
            cursor.close()
            conn.close()
            return {"success": False, "message": "Mot de passe actuel incorrect"}

        print(f"[DEBUG] ✅ Ancien mot de passe vérifié")

        # Générer le nouveau hash avec bcrypt
        new_password_bytes = new_password.encode('utf-8')
        salt = bcrypt.gensalt()
        new_hashed_password = bcrypt.hashpw(new_password_bytes, salt)
        
        # Convertir le hash bytes en string pour stockage en base
        new_hashed_password_str = new_hashed_password.decode('utf-8')
        
        print(f"[DEBUG] Nouveau hash généré avec bcrypt")
        print(f"[DEBUG]   - Hash: {new_hashed_password_str[:60]}...")

        # Mise à jour dans la table users
        cursor.execute("UPDATE users SET password=%s WHERE id=%s", 
                      (new_hashed_password_str, user_id))
        conn.commit()
        
        print(f"[DEBUG] ✅ Mot de passe mis à jour en base")
        
        cursor.close()
        conn.close()

        return {"success": True, "message": "Mot de passe mis à jour avec succès"}

     except Exception as e:
        print(f"[RPC] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        try:
            if 'conn' in locals():
                conn.rollback()
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        except:
            pass
        return {"success": False, "message": f"Erreur: {str(e)}"}
    def get_next_appointment(self, user_id):
     """
    Récupère le prochain rendez-vous à venir pour un patient
    """
     patient_id = user_id
    
     try:
        print("="*60)
        print(f"[RPC-DEBUG] 🚀 get_next_appointment() appelée")
        print(f"[RPC-DEBUG] 📋 Paramètres reçus:")
        print(f"  - user_id (patient): {patient_id}")
        print("="*60)
        
        conn = get_db_connection()
        if not conn:
            print("[RPC-DEBUG] ❌ ÉCHEC: Impossible de se connecter à la base de données")
            return {"success": False, "appointment": None, "debug": "DB connection failed"}
        
        print("[RPC-DEBUG] ✅ Connexion DB établie")
        
        cursor = conn.cursor(dictionary=True)
        
        # ÉTAPE 1: Récupérer l'ID interne du patient
        print(f"[RPC-DEBUG] 🔍 ÉTAPE 1: Recherche patient avec user_id={patient_id}")
        cursor.execute("SELECT id, nom, email FROM patients WHERE user_id=%s", (patient_id,))
        patient_row = cursor.fetchone()
        
        if not patient_row:
            print("[RPC-DEBUG] ❌ ÉCHEC: Patient introuvable dans la table patients")
            cursor.close()
            conn.close()
            return {
                "success": False, 
                "appointment": None, 
                "debug": f"Patient user_id={patient_id} non trouvé"
            }
        
        internal_patient_id = patient_row['id']
        print(f"[RPC-DEBUG] ✅ Patient trouvé:")
        print(f"  - ID interne: {internal_patient_id}")
        print(f"  - Nom: {patient_row['nom']}")
        print(f"  - Email: {patient_row['email']}")
        
        # ÉTAPE 5: Recherche finale avec la bonne condition
        print(f"[RPC-DEBUG] 🔍 ÉTAPE 5: Recherche du prochain RDV")
        cursor.execute("""
            SELECT 
                r.id,
                r.date_heure,
                m.nom as medecin_nom,
                s.nom as specialite,
                DATE(r.date_heure) as date_only,
                TIME_FORMAT(r.date_heure, '%H:%i') as time_only,
                r.statut
            FROM rendezvous r
            JOIN medecins m ON r.medecin_id = m.id
            LEFT JOIN specialisations s ON m.id_specialisation = s.id
            WHERE r.patient_id = %s 
              AND r.date_heure >= NOW()
              AND LOWER(r.statut) IN ('confirmé')
            ORDER BY r.date_heure ASC
            LIMIT 1
        """, (internal_patient_id,))
        
        next_appointment = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if next_appointment:
            print(f"[RPC-DEBUG] ✅ SUCCÈS: RDV trouvé!")
            print(f"  - ID: {next_appointment['id']}")
            print(f"  - Date brute: {next_appointment['date_heure']} (type: {type(next_appointment['date_heure'])})")
            print(f"  - date_only: {next_appointment['date_only']} (type: {type(next_appointment['date_only'])})")
            print(f"  - time_only: {next_appointment['time_only']} (type: {type(next_appointment['time_only'])})")
            print(f"  - Statut: '{next_appointment['statut']}'")
            print(f"  - Médecin: {next_appointment['medecin_nom']}")
            
            # ============================================
            # CORRECTION CRITIQUE: Convertir TOUS les dates en strings
            # ============================================
            for key in list(next_appointment.keys()):
                value = next_appointment[key]
                if value is not None:
                    if isinstance(value, (datetime, date)):
                        print(f"[RPC-DEBUG] 🔄 Conversion {key}: {value} (type: {type(value)}) -> string")
                        if isinstance(value, datetime):
                            next_appointment[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                        else:  # c'est un date
                            next_appointment[key] = value.strftime("%Y-%m-%d")
                    elif isinstance(value, Decimal):
                        # Convertir aussi les Decimal en float
                        next_appointment[key] = float(value)
            
            # Assurer que time_only est bien une string
            if next_appointment.get('time_only') and isinstance(next_appointment['time_only'], (time, timedelta)):
                if isinstance(next_appointment['time_only'], time):
                    next_appointment['time_only'] = next_appointment['time_only'].strftime("%H:%M")
                else:  # timedelta
                    hours = next_appointment['time_only'].seconds // 3600
                    minutes = (next_appointment['time_only'].seconds % 3600) // 60
                    next_appointment['time_only'] = f"{hours:02d}:{minutes:02d}"
            
            print(f"[RPC-DEBUG] 📦 Données après conversion:")
            for key, value in next_appointment.items():
                print(f"  {key}: {value} (type: {type(value)})")
            
            result = {
                "success": True,
                "appointment": next_appointment,
                "debug": {
                    "patient_found": True,
                    "query_used": "LOWER(r.statut) IN ('confirmé', 'en attente')"
                }
            }
        else:
            print(f"[RPC-DEBUG] ⚠️ ATTENTION: Aucun RDV trouvé avec les conditions actuelles")
            result = {
                "success": False,
                "appointment": None,
                "debug": {
                    "patient_found": True,
                    "message": "Aucun RDV futur avec statut 'confirmé' ou 'en attente'"
                }
            }
        
        print("[RPC-DEBUG] ✅ Connexion DB fermée")
        print("="*60)
        
        return result
    
     except Exception as e:
        print(f"[RPC-DEBUG] ❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        except:
            pass
            
        return {
            "success": False, 
            "appointment": None,
            "debug": f"Exception: {str(e)}"
        }
    def logout(self):
     """
    Gère la déconnexion (méthode simple)
    """
     print("[RPC-LOGOUT] ✅ Déconnexion traitée côté serveur")
     return {"success": True, "message": "Déconnexion réussie"}
     # ==========================================
     # MÉTHODE: get_appointment_invoice
     # ==========================================
    def get_appointment_invoice(self, user_id, appointment_id):
     """
    Récupère les détails de la facture pour un rendez-vous
     """
     patient_id = user_id
    
     try:
        print(f"[RPC] 🧾 Génération facture pour RDV {appointment_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer l'ID interne du patient
        cursor.execute("SELECT id, nom, email, telephone FROM patients WHERE user_id=%s", (patient_id,))
        patient_row = cursor.fetchone()
        if not patient_row:
            cursor.close()
            conn.close()
            return {"success": False, "message": "Patient introuvable"}
        
        internal_patient_id = patient_row['id']
        
        # Récupérer les détails complets du RDV + Médecin
        cursor.execute("""
            SELECT 
                r.id,
                r.date_heure,
                r.statut,
                r.notes,
                m.nom as medecin_nom,
                m.email as medecin_email,
                m.telephone as medecin_telephone,
                m.tarif_consultation,
                m.clinic as adresse_cabinet,
                s.nom as specialite
            FROM rendezvous r
            JOIN medecins m ON r.medecin_id = m.id
            LEFT JOIN specialisations s ON m.id_specialisation = s.id
            WHERE r.id = %s AND r.patient_id = %s
        """, (appointment_id, internal_patient_id))
        
        rdv = cursor.fetchone()
        
        if not rdv:
            cursor.close()
            conn.close()
            return {"success": False, "message": "Rendez-vous introuvable"}
        
        # Vérifier que le RDV est terminé
        if rdv['statut'].lower() != 'terminé':
            cursor.close()
            conn.close()
            return {"success": False, "message": "La facture n'est disponible que pour les RDV terminés"}
        
        # Calculer les montants
        tarif = float(rdv['tarif_consultation']) if rdv['tarif_consultation'] else 0.0
        tva_rate = 0.20  # 20% TVA
        tva_amount = tarif * tva_rate
        total_ttc = tarif + tva_amount
        
        # Générer numéro de facture
        invoice_number = f"FAC-{rdv['id']:06d}"
        
        # Formater la date
        if isinstance(rdv['date_heure'], datetime):
            rdv['date_heure'] = rdv['date_heure'].strftime("%d/%m/%Y à %H:%M")
        
        invoice_data = {
            "invoice_number": invoice_number,
            "date_emission": datetime.now().strftime("%d/%m/%Y"),
            "patient": {
                "nom": patient_row['nom'],
                "email": patient_row['email'],
                "telephone": patient_row['telephone']
            },
            "medecin": {
                "nom": rdv['medecin_nom'],
                "specialite": rdv['specialite'],
                "email": rdv['medecin_email'],
                "telephone": rdv['medecin_telephone'],
                "adresse": rdv['adresse_cabinet']
            },
            "consultation": {
                "date": rdv['date_heure'],
                "motif": rdv['notes'] or "Consultation générale"
            },
            "montants": {
                "tarif_ht": round(tarif, 2),
                "tva_rate": tva_rate * 100,
                "tva_amount": round(tva_amount, 2),
                "total_ttc": round(total_ttc, 2)
            }
        }
        
        cursor.close()
        conn.close()
        
        print(f"[RPC] ✅ Facture générée: {invoice_number}")
        return {"success": True, "invoice": invoice_data}
        
     except Exception as e:
        print(f"[RPC] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        try:
            cursor.close()
            conn.close()
        except:
            pass
        return {"success": False, "message": f"Erreur: {str(e)}"}
# ==========================================
# LANCEMENT DU SERVEUR RPC
# ==========================================
if __name__ == "__main__":
    server_rpc = ServerRPC()
    print("="*50)
    print("🚀 Serveur RPC démarré sur le port 9000")
    print("="*50)
    server_rpc.server.serve_forever()