from flask import Blueprint, render_template,request,jsonify
from app import get_db_connection
from datetime import datetime, timedelta,time
import calendar
patient = Blueprint("patient", __name__, url_prefix="/patient")

@patient.route("/accueil")
def accueil():
    return render_template("patient/accueil.html")
 
@patient.route("/dashboard")
def dashboard():
    patient_id = 1  # patient par défaut

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # pour récupérer dict au lieu de tuple

    # Nom du patient
    cursor.execute("SELECT nom FROM patients WHERE id=%s", (patient_id,))
    patient_row = cursor.fetchone()
    patient_name = patient_row['nom'] if patient_row else 'Patient'

    # Tous les rendez-vous à venir
    cursor.execute("""
        SELECT r.id, r.date_heure, r.statut, r.notes,
               m.nom AS medecin_nom, 
               m.specialite, 
               m.photo_url
        FROM rendezvous r
        JOIN medecins m ON r.medecin_id = m.id
        WHERE r.patient_id=%s AND r.date_heure >= NOW() AND r.statut != 'Annulé' And r.statut!='En attente'
        ORDER BY r.date_heure ASC
    """, (patient_id,))
    upcoming_appointments = cursor.fetchall()  # renommer pour refléter plusieurs RDV

    # Historique 3 derniers rendez-vous
    cursor.execute("""
        SELECT r.date_heure, m.nom AS medecin_nom, r.statut
        FROM rendezvous r
        JOIN medecins m ON r.medecin_id = m.id
        WHERE r.patient_id=%s
        ORDER BY r.date_heure DESC
        LIMIT 3
    """, (patient_id,))
    last_consults = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "patient/dashboard.html",
        patient_name=patient_name,
        upcoming_appointments=upcoming_appointments,  # bien refléter la variable
        last_consults=last_consults
    )


@patient.route("/mes_rdv")
def mes_rdv():
    patient_id = 1  # récupère l'id du patient connecté

    conn = get_db_connection()

    # --- Curseur pour les rendez-vous (dictionnaire) ---
    cursor_rdv = conn.cursor(dictionary=True)
    cursor_rdv.execute("""
        SELECT r.id, r.date_heure, r.statut, m.clinic, r.notes,
               m.nom AS medecin_nom, s.nom AS specialite
        FROM rendezvous r
        JOIN medecins m ON r.medecin_id = m.id
        JOIN specialisations s ON m.id_specialisation = s.id
        WHERE r.patient_id = %s
        ORDER BY r.date_heure DESC
    """, (patient_id,))
    upcoming_appointments = cursor_rdv.fetchall()
    cursor_rdv.close()

    # --- Curseur pour les spécialités (tuple classique) ---
    cursor_spec = conn.cursor()
    cursor_spec.execute("SELECT id, nom FROM specialisations")
    specialisations = cursor_spec.fetchall()
    cursor_spec.close()

    conn.close()

    return render_template(
        "patient/mes_rdv.html",
        specialisations=specialisations,
        upcoming_appointments=upcoming_appointments
    )

 

 

@patient.route("/profile")
def profile():
    return render_template("patient/profile.html")

@patient.route("/logout")
def logout():
    return render_template("patient/logout.html")

@patient.route("/prise_rdv")
def prise_rdv():
    return render_template("patient/prise_rdv.html")
   
@patient.route("/get_doctors")
def get_doctors():
    specialization_id = request.args.get('specialization')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Requête pour récupérer les docteurs de cette spécialisation
    cursor.execute("""
        SELECT id, nom 
        FROM medecins
        WHERE id_specialisation = %s
    """, (specialization_id,))
    
    docteurs = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print(f"Docteurs pour spécialisation {specialization_id}:", docteurs)  # Débogage
    
    # Retourner en JSON
    return jsonify([{
        "id": d[0], 
        "nom": f"{d[1]}"  # Nom complet
    } for d in docteurs])
@patient.route("/get_available_dates")
def get_available_dates():
    doctor_id = request.args.get("doctor_id")
    if not doctor_id:
        return jsonify({"success": False, "dates": []})

    try:
        jours_en_fr = {
            "Monday": "Lundi",
            "Tuesday": "Mardi",
            "Wednesday": "Mercredi",
            "Thursday": "Jeudi",
            "Friday": "Vendredi",
            "Saturday": "Samedi",
            "Sunday": "Dimanche"
        }

        print("Connexion à la base de données...")
        conn = get_db_connection()
        cursor = conn.cursor()

        today = datetime.today().date()
        print(f"Date actuelle : {today}")
        
        # Chercher les dates sur les 3 prochains mois
        available_dates = []
        
        for month_offset in range(0, 3):  # Mois actuel + 2 mois suivants
            # Calcul correct du mois suivant
            year = today.year
            month = today.month + month_offset
            
            # Ajuster l'année si le mois dépasse 12
            if month > 12:
                year += 1
                month -= 12
            
            _, nb_jours = calendar.monthrange(year, month)
            print(f"Recherche dans le mois {month}/{year} - {nb_jours} jours")

            # Itérer sur tous les jours du mois
            for day in range(1, nb_jours + 1):
                date_obj = datetime(year, month, day).date()
                jour_semaine = jours_en_fr[date_obj.strftime("%A")]
                date_str = date_obj.strftime("%Y-%m-%d")

                # Ignorer les dates passées
                if date_obj < today:
                    continue

                print(f"Vérification de la date : {date_str} ({jour_semaine})")

                # Vérifier les disponibilités du médecin pour ce jour
                cursor.execute("""
                    SELECT heure_debut, heure_fin
                    FROM disponibilites
                    WHERE medecin_id=%s AND jour_semaine=%s
                """, (doctor_id, jour_semaine))
                dispo_list = cursor.fetchall()

                print(f"Disponibilités trouvées pour {date_str}: {dispo_list}")

                day_has_slot = False

                # Vérification des créneaux pour la date
                for dispo in dispo_list:
                    start_time = (datetime.min + dispo[0]).time() if isinstance(dispo[0], timedelta) else dispo[0]
                    end_time = (datetime.min + dispo[1]).time() if isinstance(dispo[1], timedelta) else dispo[1]

                    if not isinstance(start_time, time) or not isinstance(end_time, time):
                        print(f"Format d'heure invalide: {start_time}, {end_time}")
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
                            print(f"Créneau libre trouvé: {slot_start}")
                            day_has_slot = True
                            break

                        current_time += timedelta(minutes=30)

                    if day_has_slot:
                        break

                if day_has_slot:
                    available_dates.append(date_str)
                    print(f"Date ajoutée: {date_str}")

        cursor.close()
        conn.close()

        print(f"Dates disponibles pour le docteur {doctor_id}: {available_dates}")
        return jsonify({"success": bool(available_dates), "dates": sorted(list(set(available_dates)))})

    except Exception as e:
        print(f"Erreur dans get_available_dates: {e}")
        return jsonify({"success": False, "dates": [], "error": str(e)})
@patient.route("/get_available_slots")
def get_available_slots():
    doctor_id = request.args.get("doctor_id")
    consultation_date = request.args.get("consultation_date")
    if not doctor_id or not consultation_date:
        return jsonify({"success": False, "slots": []})

    jours_en_fr = {
        "Monday": "Lundi",
        "Tuesday": "Mardi",
        "Wednesday": "Mercredi",
        "Thursday": "Jeudi",
        "Friday": "Vendredi",
        "Saturday": "Samedi",
        "Sunday": "Dimanche"
    }

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Obtenir le jour de la semaine en français
        date_obj = datetime.strptime(consultation_date, "%Y-%m-%d")
        jour_semaine = jours_en_fr[date_obj.strftime("%A")]

        print(f"Recherche des créneaux pour le {consultation_date} ({jour_semaine})")  # Débogage

        # Récupérer les disponibilités du médecin pour ce jour
        cursor.execute("""
            SELECT heure_debut, heure_fin
            FROM disponibilites
            WHERE medecin_id=%s AND jour_semaine=%s
        """, (doctor_id, jour_semaine))

        dispo_list = cursor.fetchall()
        slots = []

        print(f"Disponibilités trouvées: {dispo_list}")  # Débogage

        for dispo in dispo_list:
            # Gérer les différents formats d'heure (timedelta ou string)
            if isinstance(dispo[0], timedelta):
                start_time = (datetime.min + dispo[0]).time()
            else:
                # Si c'est un string, le convertir en time
                start_time = datetime.strptime(str(dispo[0]), "%H:%M:%S").time()
            
            if isinstance(dispo[1], timedelta):
                end_time = (datetime.min + dispo[1]).time()
            else:
                end_time = datetime.strptime(str(dispo[1]), "%H:%M:%S").time()

            print(f"Traitement créneau: {start_time} - {end_time}")  # Débogage

            current_time = datetime.combine(date_obj, start_time)
            end_datetime = datetime.combine(date_obj, end_time)

            while current_time < end_datetime:  # < au lieu de <= pour éviter le chevauchement
                slot_start_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
                slot_end_time = current_time + timedelta(minutes=30)
                slot_end_str = slot_end_time.strftime("%Y-%m-%d %H:%M:%S")

                # Vérifier les conflits de rendez-vous dans l'intervalle
                cursor.execute("""
                    SELECT COUNT(*) FROM rendezvous
                    WHERE medecin_id=%s AND date_heure >= %s AND date_heure < %s
                """, (doctor_id, slot_start_str, slot_end_str))
                conflict = cursor.fetchone()[0]

                if conflict == 0:
                    slot_display = current_time.strftime("%H:%M")
                    slots.append(slot_display)
                    print(f"Créneau disponible: {slot_display}")  # Débogage

                current_time += timedelta(minutes=30)

        print(f"Créneaux disponibles: {slots}")  # Débogage
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "slots": slots})

    except Exception as e:
        print(f"Erreur dans get_available_slots: {e}")  # Débogage
        cursor.close()
        conn.close()
        return jsonify({"success": False, "slots": [], "error": str(e)})
@patient.route("/book_appointment", methods=["POST"])
def book_appointment():
    jours_en_fr = {
        "Monday": "Lundi",
        "Tuesday": "Mardi",
        "Wednesday": "Mercredi",
        "Thursday": "Jeudi",
        "Friday": "Vendredi",
        "Saturday": "Samedi",
        "Sunday": "Dimanche"
    }

    # Récupérer les données du formulaire
    patient_id = 1  # À remplacer par l'ID du patient connecté
    doctor_id = request.form.get("doctor_id")
    consultation_date = request.form.get("consultation_date")
    consultation_time = request.form.get("consultation_time")
    reason = request.form.get("reason")

    if not (doctor_id and consultation_date and consultation_time and reason):
        return jsonify({"success": False, "message": "Tous les champs sont requis."})

    # Combiner date et heure
    date_heure_str = f"{consultation_date} {consultation_time}:00"
    date_heure = datetime.strptime(date_heure_str, "%Y-%m-%d %H:%M:%S")
    jour_semaine = jours_en_fr[date_heure.strftime("%A")]

    # Connexion à la DB
    conn = get_db_connection()
    cursor = conn.cursor()

    # Vérifier disponibilité du médecin
    cursor.execute("""
        SELECT * 
        FROM disponibilites
        WHERE medecin_id = %s 
          AND jour_semaine = %s
          AND heure_debut <= %s
          AND heure_fin >= %s
    """, (doctor_id, jour_semaine, consultation_time, consultation_time))
    dispo = cursor.fetchone()

    if not dispo:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Le médecin n'est pas disponible à cette heure."})

    # Vérifier conflit de rendez-vous
    cursor.execute("""
        SELECT COUNT(*) 
        FROM rendezvous
        WHERE medecin_id = %s AND date_heure = %s
    """, (doctor_id, date_heure_str))
    conflict = cursor.fetchone()[0]

    if conflict > 0:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Ce créneau est déjà pris."})
    #le patient ne peut pas prendre deux rendez vous meme day chez meme doctor
    cursor.execute("""
    SELECT COUNT(*) 
    FROM rendezvous
    WHERE patient_id = %s 
      AND medecin_id = %s 
      AND DATE(date_heure) = %s
      AND statut != 'Annulé'
""", (patient_id, doctor_id, consultation_date))

    already_has = cursor.fetchone()[0]

    if already_has > 0:
     cursor.close()
     conn.close()
     return jsonify({
        "success": False,
        "message": "Vous avez déjà un rendez-vous ce jour-là avec ce médecin."
    })
    # Insérer le rendez-vous
    try:
        cursor.execute("""
            INSERT INTO rendezvous (date_heure, patient_id, medecin_id, statut, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (date_heure_str, patient_id, doctor_id, "En attente", reason))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": str(e)})


#creer route honoraire
@patient.route("/get_honoraires")
def get_honoraires():
    doctor_id = request.args.get('doctor_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer l'honoraire du médecin
    cursor.execute("""
        SELECT id, tarif_consultation 
        FROM medecins
        WHERE id = %s
    """, (doctor_id,))
    
    medecin = cursor.fetchone()
    cursor.close()
    conn.close()
    
    print(f"Honoraire pour docteur {doctor_id}:", medecin)  # Débogage
    
    # Retourner en JSON (un seul honoraire)
    if medecin:
        return jsonify([{
            "id": medecin[0], 
            "montant": medecin[1]
        }])
    else:
        return jsonify([])
    


