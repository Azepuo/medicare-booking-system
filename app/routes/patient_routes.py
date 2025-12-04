from flask import Blueprint, render_template, request, jsonify
from app import get_db_connection
from datetime import datetime, timedelta, time
import calendar
from xmlrpc.client import ServerProxy
import xmlrpc.client
import http.client

patient = Blueprint("patient", __name__, url_prefix="/patient")

# ✅ Fonction pour créer une nouvelle connexion RPC à chaque appel
def get_rpc_server():
    """Crée une nouvelle connexion RPC avec timeout pour éviter les conflits"""
    class TimeoutTransport(xmlrpc.client.Transport):
        def __init__(self, timeout=10, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.timeout = timeout
        
        def make_connection(self, host):
            connection = http.client.HTTPConnection(host, timeout=self.timeout)
            return connection
    
    return ServerProxy(
        "http://localhost:9000/", 
        allow_none=True,
        transport=TimeoutTransport(timeout=10)
    )

@patient.route("/accueil")
def accueil():
    return render_template("patient/accueil.html")
 
@patient.route("/dashboard")
def dashboard():
    patient_id = 1  # à remplacer par session['patient_id']

    try:
        # Appel RPC
        rpc_server = get_rpc_server()
        rpc_data = rpc_server.get_dashboard(patient_id)
        patient_name = rpc_data['patient_info']['nom']
        upcoming_appointments = rpc_data['upcoming_appointments']
        last_consults = rpc_data['past_appointments']
    except Exception as e:
        print("Erreur RPC:", e)
        # Fallback si RPC échoue
        patient_name = "Patient"
        upcoming_appointments = []
        last_consults = []

    return render_template(
        "patient/dashboard.html",
        patient_name=patient_name,
        upcoming_appointments=upcoming_appointments,
        last_consults=last_consults
    )
@patient.route('/rdv/details/<int:rdv_id>', methods=['GET'])
def get_rdv_details(rdv_id):
    try:
        print("="*50)
        print(f"[RDV_DETAILS] Récupération détails pour RDV: {rdv_id}")
        
        patient_id = 1  # À remplacer par session['patient_id']
        
        # Vérifier que le RDV appartient au patient (sécurité)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT patient_id FROM rendezvous WHERE id = %s
        """, (rdv_id,))
        rdv_patient = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not rdv_patient or rdv_patient[0] != patient_id:
            return jsonify({
                'success': False,
                'message': 'Accès non autorisé'
            }), 403

        # 🔴 CORRECTION : Créer une connexion RPC
        rpc_server = get_rpc_server()  # ← AJOUTEZ CETTE LIGNE !
        
        # Appel RPC
        result = rpc_server.get_rendezvous_details(rdv_id)
        
        print(f"[RDV_DETAILS] Résultat RPC: {result}")
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Rendez-vous introuvable')
            }), 404
            
    except Exception as e:
        print(f"[RDV_DETAILS] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500

@patient.route("/mes_rdv")
def mes_rdv():
    patient_id = 1  # à remplacer par session['patient_id']

    try:
        print("="*50)
        print(f"[ROUTE] Récupération RDV pour patient_id: {patient_id}")
        print("="*50)
        
        # Appel RPC
        rpc_server = get_rpc_server()
        rpc_data = rpc_server.get_all_appointments(patient_id)
        
        print(f"[ROUTE] Type de rpc_data: {type(rpc_data)}")
        print(f"[ROUTE] rpc_data reçu: {rpc_data}")
        
        if isinstance(rpc_data, dict) and rpc_data.get("success") is False:
            print(f"[RPC] Erreur récupération rendez-vous: {rpc_data.get('message')}")
            all_appointments = []
        else:
            all_appointments = rpc_data

        print(f"[ROUTE] Nombre de RDV: {len(all_appointments) if all_appointments else 0}")
        if all_appointments and len(all_appointments) > 0:
            print(f"[ROUTE] Premier RDV brut: {all_appointments[0]}")

        # Sécuriser et formater les données
        for i, rdv in enumerate(all_appointments):
            print(f"\n[ROUTE] Traitement RDV {i+1}:")
            print(f"  - ID: {rdv.get('id')}")
            print(f"  - date_heure avant: {rdv.get('date_heure')} (type: {type(rdv.get('date_heure'))})")
            
            # date_heure
            if isinstance(rdv.get("date_heure"), datetime):
                rdv["date_heure"] = rdv["date_heure"].strftime("%Y-%m-%d %H:%M")
            elif not rdv.get("date_heure"):
                rdv["date_heure"] = ""

            print(f"  - date_heure après: {rdv.get('date_heure')}")
            print(f"  - date_only: {rdv.get('date_only')}")
            print(f"  - time_only: {rdv.get('time_only')}")

            # time_only
            if not rdv.get("time_only"):
                try:
                    rdv["time_only"] = rdv["date_heure"].split(" ")[1] if rdv["date_heure"] else ""
                except:
                    rdv["time_only"] = ""
                    print(f"  ⚠️ Erreur extraction time_only")

            # Autres champs jamais None
            for key in ["statut", "clinic", "notes", "medecin_id", "medecin_nom", "specialite", "date_only"]:
                if rdv.get(key) is None:
                    rdv[key] = ""
                    print(f"  ⚠️ Champ {key} était None, défini à ''")

        print(f"\n[ROUTE] Tous les RDV après formatage:")
        for i, rdv in enumerate(all_appointments):
            print(f"  RDV {i+1}: {rdv}")

        # Récupérer les spécialités pour le filtre
        conn = get_db_connection()
        cursor_spec = conn.cursor()
        cursor_spec.execute("SELECT id, nom FROM specialisations")
        specialisations = cursor_spec.fetchall()
        print(f"[ROUTE] Spécialisations: {specialisations}")
        cursor_spec.close()
        conn.close()

    except Exception as e:
        print(f"[Mes RDV] ❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        all_appointments = []
        specialisations = []

    print(f"\n[ROUTE] ✅ Envoi au template:")
    print(f"  - Nombre de RDV: {len(all_appointments)}")
    print(f"  - Nombre de spécialisations: {len(specialisations)}")
    print("="*50)

    return render_template(
        "patient/mes_rdv.html",
        specialisations=specialisations,
        upcoming_appointments=all_appointments
    )

@patient.route("/update_appointment", methods=["POST"])
def update_appointment():
    try:
        # Récupérer les données du formulaire
        appointment_id = request.form.get("id")
        medecin_id = request.form.get("medecin_id")
        date = request.form.get("date")
        time_str = request.form.get("time")
        notes = request.form.get("notes", "")
        
        patient_id = 1  # À remplacer par l'ID du patient connecté

        print("="*50)
        print(f"[UPDATE] Mise à jour RDV:")
        print(f"  - ID: {appointment_id}")
        print(f"  - Médecin: {medecin_id}")
        print(f"  - Date: {date}")
        print(f"  - Heure: {time_str}")
        print(f"  - Patient: {patient_id}")

        # Validation
        if not (appointment_id and medecin_id and date and time_str):
            return jsonify({
                "success": False, 
                "message": "Tous les champs sont requis."
            })

        # Appel RPC
        rpc_server = get_rpc_server()
        result = rpc_server.update_appointment(
            appointment_id, 
            medecin_id, 
            date, 
            time_str, 
            notes, 
            patient_id
        )
        
        print(f"[UPDATE] ✅ Résultat RPC: {result}")
        return jsonify(result)

    except Exception as e:
        print(f"[UPDATE] ❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "message": f"Erreur de traitement: {str(e)}"
        })

@patient.route("/cancel_appointment", methods=["POST"])
def cancel_appointment():
    try:
        # Récupérer les données
        data = request.get_json()
        appointment_id = data.get("appointment_id")
        
        patient_id = 1  # À remplacer par session['patient_id']

        print("="*50)
        print(f"[CANCEL] Annulation RDV:")
        print(f"  - RDV ID: {appointment_id}")
        print(f"  - Patient ID: {patient_id}")

        # Validation
        if not appointment_id:
            return jsonify({
                "success": False, 
                "message": "ID du rendez-vous manquant"
            })

        # Appel RPC
        rpc_server = get_rpc_server()
        result = rpc_server.cancel_appointment(appointment_id)
        
        print(f"[CANCEL] ✅ Résultat RPC: {result}")
        return jsonify(result)

    except Exception as e:
        print(f"[CANCEL] ❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "message": f"Erreur de traitement: {str(e)}"
        })

@patient.route("/profile")
def profile():
    patient_id = 1  # à remplacer par session['patient_id']

    try:
        print("="*50)
        print(f"[PROFILE] Appel RPC pour profil patient:")
        print(f"  - Patient ID: {patient_id}")

        # Appel RPC
        rpc_server = get_rpc_server()
        rpc_data = rpc_server.get_profile_local(patient_id)
        
        print(f"[PROFILE] ✅ Données RPC reçues: {rpc_data}")
        
        if isinstance(rpc_data, dict) and 'patient_info' in rpc_data:
            patient_data = rpc_data['patient_info']
            stats = {
                "rdv_count": rpc_data.get('total_rdv', 0),
                "medecins_count": 0,  # À calculer si nécessaire
                "pending_count": 0    # À calculer si nécessaire
            }
        else:
            print(f"[PROFILE] ⚠️ Structure de données invalide")
            patient_data = {"nom": "", "email": "", "telephone": ""}
            stats = {"rdv_count": 0, "medecins_count": 0, "pending_count": 0}

    except Exception as e:
        print(f"[PROFILE] ❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback minimal
        patient_data = {"nom": "", "email": "", "telephone": ""}
        stats = {"rdv_count": 0, "medecins_count": 0, "pending_count": 0}

    print(f"[PROFILE] ✅ Données envoyées au template:")
    print(f"  - Patient: {patient_data.get('nom')}")
    print(f"  - RDV count: {stats.get('rdv_count')}")
    print("="*50)

    return render_template("patient/profile.html", patient=patient_data, stats=stats)

@patient.route("/update_profile", methods=["POST"])
def update_profile():
    try:
        # Récupérer les données
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        telephone = request.form.get("telephone", "").strip()
        
        patient_id = 1  # À remplacer par l'ID du patient connecté

        print("="*50)
        print(f"[UPDATE_PROFILE] Appel RPC pour mise à jour profil")

        # Validation basique
        if not (nom and email and telephone):
            return jsonify({
                "success": False, 
                "message": "Tous les champs sont requis."
            })

        # Appel RPC
        rpc_server = get_rpc_server()
        result = rpc_server.update_profile(patient_id, nom, email, telephone)
        
        print(f"[UPDATE_PROFILE] Résultat: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"[UPDATE_PROFILE] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la mise à jour: {str(e)}"
        })

@patient.route("/logout")
def logout():
    return render_template("patient/logout.html")

@patient.route("/prise_rdv")
def prise_rdv():
    return render_template("patient/prise_rdv.html")

@patient.route("/get_doctors")
def get_doctors():
    patient_id = 1  # à remplacer par session['patient_id']
    specialization_id = request.args.get('specialization')

    try:
        print("="*50)
        print(f"[GET_DOCTORS] Récupération médecins:")
        print(f"  - Patient: {patient_id}")
        print(f"  - Spécialisation: {specialization_id}")

        if not specialization_id:
            return jsonify([])

        # Appel RPC
        rpc_server = get_rpc_server()
        result = rpc_server.get_doctors_local(specialization_id)
        
        print(f"[GET_DOCTORS] ✅ Résultat RPC: {len(result) if isinstance(result, list) else 'N/A'}")
        
        # Vérifier le type de retour
        if isinstance(result, list):
            return jsonify(result)
        elif isinstance(result, dict) and result.get("success") is False:
            print(f"[GET_DOCTORS] ⚠️ RPC échoué: {result.get('message')}")
            return jsonify([])
        else:
            return jsonify([])

    except Exception as e:
        print(f"[GET_DOCTORS] ❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])

# Ajouter UNIQUEMENT cette route dans votre fichier patient_routes.py
# Ajouter UNIQUEMENT cette route dans votre fichier patient_routes.py

@patient.route("/get_appointment_review/<int:appointment_id>")
def get_appointment_review(appointment_id):
    """
    Récupère l'avis existant pour un rendez-vous (si existe)
    """
    try:
        patient_id = 1  # À remplacer par session['patient_id']
        
        print(f"[GET_REVIEW] Vérification avis pour RDV {appointment_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                a.id,
                a.note,
                a.commentaire,
                a.date_avis
            FROM avis a
            WHERE a.rendezvous_id = %s AND a.patient_id = %s
        """, (appointment_id, patient_id))
        
        existing_review = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if existing_review:
            # Formater la date
            if isinstance(existing_review.get("date_avis"), datetime):
                existing_review["date_avis"] = existing_review["date_avis"].strftime("%Y-%m-%d %H:%M")
            
            print(f"[GET_REVIEW] ✅ Avis existant trouvé (ID: {existing_review['id']})")
            return jsonify({
                "success": True,
                "has_review": True,
                "review": existing_review
            })
        else:
            print(f"[GET_REVIEW] ℹ️ Aucun avis existant")
            return jsonify({
                "success": True,
                "has_review": False
            })
        
    except Exception as e:
        print(f"[GET_REVIEW] ❌ Erreur: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@patient.route("/submit_review", methods=["POST"])
def submit_review():
    """
    Route pour soumettre un avis patient
    """
    try:
        patient_id = 1  # À remplacer par session['patient_id']
        
        # Récupérer les données JSON
        data = request.get_json()
        
        appointment_id = data.get("appointment_id")
        rating = data.get("rating")
        comment = data.get("comment")
        
        print("="*50)
        print(f"[SUBMIT_REVIEW] Soumission d'avis:")
        print(f"  - Patient: {patient_id}")
        print(f"  - RDV: {appointment_id}")
        print(f"  - Note: {rating}")
        print(f"  - Commentaire: {comment[:50] if comment else 'N/A'}...")
        
        # Validation côté serveur
        if not appointment_id:
            return jsonify({
                "success": False,
                "message": "ID du rendez-vous manquant"
            }), 400
        
        if not rating:
            return jsonify({
                "success": False,
                "message": "La note est obligatoire"
            }), 400
        
        if not comment or len(comment.strip()) < 10:
            return jsonify({
                "success": False,
                "message": "Le commentaire doit contenir au moins 10 caractères"
            }), 400
        
        # Récupérer le médecin_id depuis le rendez-vous
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT medecin_id, statut 
            FROM rendezvous 
            WHERE id = %s AND patient_id = %s
        """, (appointment_id, patient_id))
        
        rdv_info = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not rdv_info:
            return jsonify({
                "success": False,
                "message": "Rendez-vous introuvable"
            }), 404
        
        medecin_id = rdv_info[0]
        
        # Appel RPC pour enregistrer l'avis
        rpc_server = get_rpc_server()
        result = rpc_server.save_patient_review(
            patient_id,
            medecin_id,
            appointment_id,
            rating,
            comment
        )
        
        print(f"[SUBMIT_REVIEW] ✅ Résultat RPC: {result}")
        print("="*50)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        print(f"[SUBMIT_REVIEW] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "message": f"Erreur serveur: {str(e)}"
        }), 500
@patient.route("/get_available_slots")
def get_available_slots():
    patient_id = 1  # à remplacer par session['patient_id']
    doctor_id = request.args.get("doctor_id")
    consultation_date = request.args.get("consultation_date")

    try:
        print("="*50)
        print(f"[GET_AVAILABLE_SLOTS] Récupération créneaux:")
        print(f"  - Patient: {patient_id}")
        print(f"  - Médecin: {doctor_id}")
        print(f"  - Date: {consultation_date}")

        if not doctor_id or not consultation_date:
            return jsonify({"success": False, "slots": []})

        # Appel RPC
        rpc_server = get_rpc_server()
        result = rpc_server.get_available_slots_local(doctor_id, consultation_date)
        
        print(f"[GET_AVAILABLE_SLOTS] ✅ Résultat RPC: {result}")
        
        if isinstance(result, dict) and "slots" in result:
            return jsonify(result)
        elif isinstance(result, list):
            return jsonify({"success": True, "slots": result})
        else:
            return jsonify({"success": False, "slots": []})

    except Exception as e:
        print(f"[GET_AVAILABLE_SLOTS] ❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "slots": []})

@patient.route("/book_appointment", methods=["POST"])
def book_appointment_route():
    patient_id = 1  # à remplacer par session['patient_id']

    try:
        # Récupérer les données du formulaire
        doctor_id = request.form.get("doctor_id")
        consultation_date = request.form.get("consultation_date")
        consultation_time = request.form.get("consultation_time")
        reason = request.form.get("reason", "")

        print("="*50)
        print(f"[BOOK] Prise de RDV:")
        print(f"  - Patient ID: {patient_id}")
        print(f"  - Médecin ID: {doctor_id}")
        print(f"  - Date: {consultation_date}")
        print(f"  - Heure: {consultation_time}")
        print(f"  - Motif: {reason[:50]}...")

        # Validation
        if not all([doctor_id, consultation_date, consultation_time]):
            return jsonify({
                "success": False, 
                "message": "Tous les champs sont requis."
            })

        # Appel RPC
        rpc_server = get_rpc_server()
        result = rpc_server.book_appointment(
            patient_id, 
            doctor_id, 
            consultation_date, 
            consultation_time,
            reason
        )
        
        print(f"[BOOK] ✅ Résultat RPC: {result}")
        return jsonify(result)

    except Exception as e:
        print(f"[BOOK] ❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "message": f"Erreur de traitement: {str(e)}"
        })

@patient.route("/get_honoraires")
def get_honoraires():
    patient_id = 1  # à remplacer par session['patient_id']
    doctor_id = request.args.get('doctor_id')

    try:
        print("="*50)
        print(f"[GET_HONORAIRES] Récupération honoraires:")
        print(f"  - Patient: {patient_id}")
        print(f"  - Médecin: {doctor_id}")

        if not doctor_id:
            return jsonify([])

        # Appel RPC avec retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"[GET_HONORAIRES] Tentative {attempt + 1}/{max_retries}")
                rpc_server = get_rpc_server()
                result = rpc_server.get_honoraires_local(doctor_id)
                
                print(f"[GET_HONORAIRES] ✅ Résultat RPC: {result}")
                
                # Vérifier le type de retour
                if isinstance(result, dict) and "honoraire" in result:
                    return jsonify([{"id": doctor_id, "montant": result["honoraire"]}])
                elif isinstance(result, list):
                    return jsonify(result)
                elif isinstance(result, dict) and result.get("success") is False:
                    print(f"[GET_HONORAIRES] ⚠️ RPC échoué: {result.get('message')}")
                    return jsonify([])
                else:
                    return jsonify([])
                    
            except Exception as rpc_error:
                print(f"[GET_HONORAIRES] ⚠️ Erreur tentative {attempt + 1}: {rpc_error}")
                if attempt == max_retries - 1:
                    raise
                import time
                time.sleep(0.3)

    except Exception as e:
        print(f"[GET_HONORAIRES] ❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])

@patient.route("/get_available_dates")
def get_available_dates():
    patient_id = 1  # à remplacer par session['patient_id']
    doctor_id = request.args.get("doctor_id")

    try:
        print("="*50)
        print(f"[GET_AVAILABLE_DATES] Récupération dates disponibles:")
        print(f"  - Patient: {patient_id}")
        print(f"  - Médecin: {doctor_id}")

        if not doctor_id:
            return jsonify({"success": False, "dates": []})

        # Appel RPC avec retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"[GET_AVAILABLE_DATES] Tentative {attempt + 1}/{max_retries}")
                rpc_server = get_rpc_server()
                result = rpc_server.get_available_dates_local(doctor_id)
                
                print(f"[GET_AVAILABLE_DATES] ✅ Résultat RPC: {result}")
                
                if isinstance(result, dict) and "dates" in result:
                    return jsonify(result)
                else:
                    return jsonify({"success": False, "dates": []})
                    
            except Exception as rpc_error:
                print(f"[GET_AVAILABLE_DATES] ⚠️ Erreur tentative {attempt + 1}: {rpc_error}")
                if attempt == max_retries - 1:
                    raise
                import time
                time.sleep(0.3)

    except Exception as e:
        print(f"[GET_AVAILABLE_DATES] ❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "dates": []})