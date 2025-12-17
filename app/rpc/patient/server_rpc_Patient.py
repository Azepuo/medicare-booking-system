import xmlrpc.server
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta, time, date
import calendar

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

    def save_patient_review(self, patient_id, medecin_id, appointment_id, rating, comment):
     """
    Enregistre un avis patient pour un médecin
    Args:
        patient_id: ID du patient
        medecin_id: ID du médecin
        appointment_id: ID du rendez-vous
        rating: Note de 1 à 5
        comment: Commentaire du patient
    Returns:
        dict: {"success": True/False, "message": "..."}
    """
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

    # Méthode pour afficher la page d'accueil du patient
    def get_patient_info(self, patient_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT nom, email
                FROM patients
                WHERE id = %s
            """, (patient_id,))
            patient_info = cursor.fetchone()
            if patient_info is None:
                print(f"[DEBUG] ⚠️ Aucun patient trouvé avec id={patient_id}")
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
        

    # Méthode pour afficher le tableau de bord du patient
    def get_dashboard(self, patient_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT nom, email FROM patients WHERE user_id=%s", (patient_id,))
            patient_info = cursor.fetchone()
            if patient_info is None:
                patient_info = {"nom": "", "email": ""} 
            
            # Récupérer les prochains rendez-vous
            cursor.execute("""
                SELECT r.id, r.date_heure, r.statut, r.notes,
                    m.nom AS medecin_nom, 
                    m.photo_url,
                    s.nom AS specialite
                FROM rendezvous r
                JOIN medecins m ON r.medecin_id = m.id
                Join specialisations s ON m.id_specialisation=s.id
                WHERE r.patient_id=%s AND r.date_heure >= NOW() AND r.statut NOT IN ('Annulé', 'En attente', 'terminé')
                ORDER BY r.date_heure ASC
            """, (patient_id,))
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
            """, (patient_id,))
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
    # Méthode pour afficher tous les rendez-vous du patient
    def get_all_appointments(self, patient_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    r.id, 
                    r.date_heure, 
                    r.statut,  
                    m.clinic,
                    r.notes,
                    m.id as medecin_id,
                    m.nom AS medecin_nom, 
                    s.nom AS specialite,
                    DATE(r.date_heure) as date_only,
                    TIME_FORMAT(r.date_heure, '%H:%i') as time_only
                FROM rendezvous r
                JOIN medecins m ON r.medecin_id = m.id
                JOIN specialisations s ON m.id_specialisation = s.id
                WHERE r.patient_id = %s
                ORDER BY r.date_heure DESC
            """, (patient_id,))
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

    # Méthode pour mettre à jour un rendez-vous existant
    def update_appointment(self, appointment_id, medecin_id, date, time_str, notes, patient_id):
        try:
            if not (appointment_id and medecin_id and date and time_str):
                return {"success": False, "message": "Tous les champs sont requis."}

            date_heure_str = f"{date} {time_str}:00"

            conn = get_db_connection()
            cursor = conn.cursor()

            # Vérification si le patient a déjà un rendez-vous pour ce médecin et cette date
            cursor.execute("""
                SELECT COUNT(*) 
                FROM rendezvous
                WHERE patient_id = %s 
                  AND medecin_id = %s 
                  AND DATE(date_heure) = %s
                  AND statut != 'Annulé'
                  AND id != %s
            """, (patient_id, medecin_id, date, appointment_id))

            already_has = cursor.fetchone()[0]
            if already_has > 0:
                cursor.close()
                conn.close()
                return {"success": False, "message": "Vous avez déjà un rendez-vous ce jour-là avec ce médecin."}

            # Vérification du conflit de créneaux horaires
            cursor.execute("""
                SELECT COUNT(*) 
                FROM rendezvous
                WHERE medecin_id = %s 
                  AND date_heure = %s
                  AND id != %s
            """, (medecin_id, date_heure_str, appointment_id))
            conflict = cursor.fetchone()[0]

            if conflict > 0:
                cursor.close()
                conn.close()
                return {"success": False, "message": "Ce créneau est déjà pris par un autre patient."}

            # Mise à jour du rendez-vous
            cursor.execute("""
                UPDATE rendezvous
                SET medecin_id = %s, date_heure = %s, notes = %s, statut="En attente"
                WHERE id = %s
            """, (medecin_id, date_heure_str, notes, appointment_id))

            conn.commit()
            cursor.close()
            conn.close()

            return {"success": True}
        except Error as e:
            return {"success": False, "message": str(e)}

    # Méthode pour annuler un rendez-vous existant
    def cancel_appointment(self, appointment_id):
        try:
            if not appointment_id:
                return {"success": False, "message": "ID du rendez-vous manquant"}

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE rendezvous 
                SET statut = 'Annulé' 
                WHERE id = %s
            """, (appointment_id,))

            conn.commit()
            cursor.close()
            conn.close()

            return {"success": True, "message": "Rendez-vous annulé avec succès"}
        except Error as e:
            return {"success": False, "message": str(e)}

    # Méthode pour afficher le profil du patient
    def get_profile_local(self, patient_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nom, email, telephone FROM patients WHERE user_id=%s", (patient_id,))
            patient_info = cursor.fetchone()

            cursor.execute("SELECT COUNT(*) as rdv_count FROM rendezvous r JOIN patients p ON r.patient_id = p.id where p.user_id=%s", (patient_id,))
            rdv_count = cursor.fetchone()

            cursor.close()
            conn.close()

            return {
                "patient_info": patient_info,
                "total_rdv": rdv_count["rdv_count"]
            }
        except Error as e:
            return {"success": False, "message": str(e)}

    # Méthode pour mettre à jour les informations du profil du patient
    def update_profile(self, patient_id, nom, email, telephone):
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

    # Méthode pour afficher la page de déconnexion
    def logout(self):
        return {"success": True, "message": "Déconnexion réussie"}
    
    # Méthode pour récupérer les médecins par spécialisation
    def get_doctors_local(self, specialization_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nom 
                FROM medecins
                WHERE id_specialisation = %s
            """, (specialization_id,))
            doctors = cursor.fetchall()
            cursor.close()
            conn.close()
            return doctors
        except Error as e:
            return {"success": False, "message": str(e)}

    # Méthode pour récupérer les créneaux horaires disponibles
    def get_available_slots_local(self, doctor_id, consultation_date):
        try:
            print(f"[RPC] get_available_slots_local pour médecin {doctor_id} le {consultation_date}")

            jours_en_fr = {
                "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
                "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi",
                "Sunday": "Dimanche"
            }

            conn = get_db_connection()
            cursor = conn.cursor()

            date_obj = datetime.strptime(consultation_date, "%Y-%m-%d")
            jour_semaine = jours_en_fr[date_obj.strftime("%A")]

            # Récupérer les disponibilités
            cursor.execute("""
                SELECT heure_debut, heure_fin
                FROM disponibilites
                WHERE medecin_id=%s AND jour_semaine=%s
            """, (doctor_id, jour_semaine))

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
                    """, (doctor_id, slot_start_str, slot_end_str))
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

    # Méthode pour réserver un rendez-vous
       # Méthode pour réserver un rendez-vous
    def book_appointment(self, patient_id, doctor_id, consultation_date, consultation_time, reason=""):
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

            # 1. Vérifier si le médecin existe
            cursor.execute("SELECT id, nom FROM medecins WHERE user_id = %s", (doctor_id,))
            medecin = cursor.fetchone()
            if not medecin:
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "message": "Médecin non trouvé."
                }
            print(f"[RPC] Médecin trouvé: {medecin[1]}")

            # 2. Vérifier conflit de rendez-vous (créneau déjà pris)
            db_date_heure_str = date_heure.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[RPC] Vérification conflit pour: {db_date_heure_str}")
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM rendezvous
                WHERE medecin_id = %s 
                  AND date_heure = %s
                  AND statut != 'Annulé'
            """, (doctor_id, db_date_heure_str))
            
            conflict = cursor.fetchone()[0]
            print(f"[RPC] Conflits trouvés: {conflict}")

            if conflict > 0:
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "message": "Ce créneau est déjà pris par un autre patient."
                }

            # 3. Vérifier si le patient a déjà un RDV ce jour avec ce médecin
            cursor.execute("""
                SELECT COUNT(*) 
                FROM rendezvous
                WHERE patient_id = %s 
                  AND medecin_id = %s 
                  AND DATE(date_heure) = DATE(%s)
                  AND statut != 'Annulé'
            """, (patient_id, doctor_id, db_date_heure_str))

            already_has = cursor.fetchone()[0]
            print(f"[RPC] RDV existants ce jour: {already_has}")

            if already_has > 0:
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "message": "Vous avez déjà un rendez-vous ce jour-là avec ce médecin."
                }

            # 4. Insérer le rendez-vous
            cursor.execute("""
                INSERT INTO rendezvous (date_heure, patient_id, medecin_id, statut, notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (db_date_heure_str, patient_id, doctor_id, "En attente", reason))
            
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
            
            # Annuler en cas d'erreur
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
    # Méthode pour récupérer les honoraires d'un médecin
    def get_honoraires_local(self, doctor_id):
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
                return [{"id": medecin[0], "montant":tarif}]
            else:
                print(f"[RPC] ⚠️ Médecin non trouvé")
                return []
            
        except Exception as e:
            print(f"[RPC] ❌ Erreur get_honoraires_local: {e}")
            return []

    # Méthode pour récupérer les dates disponibles
    def get_available_dates_local(self, doctor_id):
        try:
            print(f"[RPC] get_available_dates_local pour médecin {doctor_id}")

            jours_en_fr = {
                "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
                "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi",
                "Sunday": "Dimanche"
            }

            conn = get_db_connection()
            cursor = conn.cursor()

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
                    
                    # Ignorer les dates passées
                    if date_obj < today:
                        continue
                    
                    jour_semaine = jours_en_fr[date_obj.strftime("%A")]
                    date_str = date_obj.strftime("%Y-%m-%d")

                    # Vérifier les disponibilités
                    cursor.execute("""
                        SELECT heure_debut, heure_fin
                        FROM disponibilites
                        WHERE medecin_id=%s AND jour_semaine=%s
                    """, (doctor_id, jour_semaine))
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
                            """, (doctor_id, slot_start, slot_end))
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
     # Dans server_rpc.py - Ajouter cette méthode à votre classe RPC
     # Ajouter UNIQUEMENT cette méthode dans votre classe ServerRPC dans server_rpc.py
     # Ajouter UNIQUEMENT cette méthode dans votre classe ServerRPC dans server_rpc.py
# Ajouter UNIQUEMENT cette méthode dans votre classe ServerRPC dans server_rpc.py
    def get_rendezvous_details(self, rdv_id):
       """
        Récupère les détails complets d'un rendez-vous
        Compatible avec la nouvelle structure de BD (sans photo_url, specialite, annees_experience, clinic)
      """
       try:
        print(f"[RPC] 🔍 Récupération des détails du rendez-vous {rdv_id}")
        
        conn = get_db_connection()
        if not conn:
            print("[RPC] ❌ Échec de connexion à la BD")
            return {
                "success": False,
                "message": "Erreur de connexion à la base de données"
            }
        
        cursor = conn.cursor(dictionary=True)
        
        # ✅ REQUÊTE CORRIGÉE avec jointure sur specialisations
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
        
        # Formater la date si nécessaire
        if isinstance(rdv.get("date_heure"), datetime):
            rdv["date_heure"] = rdv["date_heure"].strftime("%Y-%m-%d %H:%M")
        
        # Convertir tous les objets date/datetime en strings
        for key, value in rdv.items():
            if isinstance(value, (datetime, date)):
                rdv[key] = value.strftime(
                    "%Y-%m-%d %H:%M" if isinstance(value, datetime) else "%Y-%m-%d"
                )
        
        # Assurer que les valeurs None sont remplacées par des chaînes vides
        # ET convertir les Decimal en float pour XML-RPC
        from decimal import Decimal
        
        for key in rdv.keys():
            if rdv[key] is None:
                rdv[key] = ""
            elif isinstance(rdv[key], Decimal):
                rdv[key] = float(rdv[key])  # ✅ CORRECTION: Convertir Decimal en float
        
        print(f"[RPC] ✅ Détails du rendez-vous {rdv_id} récupérés")
        print(f"[RPC]    - Médecin: {rdv['medecin_nom']}")
        print(f"[RPC]    - Spécialité: {rdv['specialite']}")
        print(f"[RPC]    - Date: {rdv['date_heure']}")
        print(f"[RPC]    - Statut: {rdv['statut']}")
        print(f"[RPC]    - Tarif: {rdv['tarif_consultation']}")
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": rdv
        }
        
       except mysql.connector.Error as db_error:
        print(f"[RPC] ❌ Erreur SQL dans get_rendezvous_details: {db_error}")
        print(f"[RPC]    Code erreur: {db_error.errno}")
        print(f"[RPC]    Message SQL: {db_error.msg}")
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
        print(f"[RPC] ❌ Erreur inattendue dans get_rendezvous_details: {e}")
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
    def mark_notification_as_read(self, notification_id):
        """
        Marque une notification comme lue
        Args:
            notification_id: ID de la notification
        Returns:
            dict: {"success": True/False}
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE notifications
                SET lue = TRUE, date_lecture = NOW()
                WHERE id = %s
            """, (notification_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"[RPC] ✅ Notification {notification_id} marquée comme lue")
            return {"success": True}
            
        except Exception as e:
            print(f"[RPC] ❌ Erreur mark_notification_as_read: {e}")
            return {"success": False, "message": str(e)}
    
    def get_unread_count(self, patient_id):
        """
        Compte les notifications non lues
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM notifications
                WHERE patient_id = %s AND lue = FALSE
            """, (patient_id,))
            
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            print(f"[RPC] ✅ Patient {patient_id} a {count} notifications non lues")
            return {"success": True, "count": count}
            
        except Exception as e:
            print(f"[RPC] ❌ Erreur get_unread_count: {e}")
            return {"success": False, "count": 0}
    def get_notifications(self, patient_id, limit):
     """
    Récupère les dernières notifications d'un patient
    """
     try:
        print("="*70)
        print(f"[DEBUG] 🚀 Entrée dans get_notifications(patient_id={patient_id}, limit={limit})")

        # Vérifier la connexion à la base
        conn = get_db_connection()
        if conn is None:
            print("[DEBUG] ❌ Connexion DB échouée !")
            return {"success": False, "notifications": []}
        else:
            print("[DEBUG] ✅ Connexion DB établie")

        cursor = conn.cursor(dictionary=True)

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
        """, (patient_id, limit))

        notifications = cursor.fetchall()
        print(f"[DEBUG] 📦 Résultats bruts récupérés: {len(notifications)} ligne(s)")

        # Détail de chaque notification
        for i, notif in enumerate(notifications, 1):
            print(f"   🔹 Notification {i}: {notif}")

        # Si aucune notification
        if not notifications:
            print("[DEBUG] ⚠️ Aucune notification trouvée pour ce patient !")

        # Vérifier les types de données
        for notif in notifications:
            if isinstance(notif.get("date_creation"), datetime):
                notif["date_creation"] = notif["date_creation"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                print(f"[DEBUG] 🕓 Attention: date_creation n'est pas un datetime -> {notif.get('date_creation')}")

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

   
    # Lancer le serveur RPC
if __name__ == "__main__":
    server_rpc = ServerRPC()
    print("Serveur RPC démarré sur le port 9000")
    server_rpc.server.serve_forever()
