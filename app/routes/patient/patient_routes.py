from flask import Blueprint, render_template, request, jsonify,redirect
from app import get_db_connection
from datetime import datetime, timedelta, time
import calendar
from xmlrpc.client import ServerProxy
import xmlrpc.client
import http.client
import jwt
SECRET_KEY = "secret123"  # ⚠️ Identique à Auth et server_rpc
def get_current_user():
    """
    Extrait user_id et role depuis le cookie JWT
    Returns:
        tuple: (user_id, role) ou (None, None)
    """
    token = request.cookies.get("access_token")

    if not token:
        print("[JWT] ❌ Aucun token trouvé")
        return None, None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        role = payload.get("role")
        
        print(f"[JWT] ✅ User authentifié: user_id={user_id}, role={role}")
        return user_id, role
        
    except jwt.ExpiredSignatureError:
        print("[JWT] ❌ Token expiré")
        return None, None
    except jwt.InvalidTokenError as e:
        print(f"[JWT] ❌ Token invalide: {e}")
        return None, None
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

@patient.route("/get_unread_count")
def get_unread_count():
    """Route pour récupérer le nombre de notifications non lues"""
    # 🔒 Vérifier authentification
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({"success": False, "count": 0, "error": "UNAUTHORIZED"})
    
    try:
        rpc_server = get_rpc_server()
        result = rpc_server.get_unread_count(user_id)
        return jsonify(result)
    except Exception as e:
        print(f"[GET_UNREAD_COUNT] ❌ Erreur: {e}")
        return jsonify({"success": False, "count": 0})

@patient.route("/get_notifications")
def get_notifications():
    """Récupère les notifications du patient"""
    # 🔒 Vérifier authentification
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({"success": False, "notifications": [], "error": "UNAUTHORIZED"})
    
    try:
        print(f"[GET_NOTIFICATIONS] Récupération pour patient {user_id}")
        
        rpc_server = get_rpc_server()
        result = rpc_server.get_notifications(user_id,10)
        
        return jsonify(result)
    except Exception as e:
        print(f"[GET_NOTIFICATIONS] ❌ Erreur: {e}")
        return jsonify({"success": False, "notifications": []})

@patient.route("/mark_notification_read/<int:notif_id>", methods=["POST"])
def mark_notification_read(notif_id):
    """Marque une notification comme lue"""
    # 🔒 Vérifier authentification
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({"success": False, "error": "UNAUTHORIZED"})
    try:
        print(f"[MARK_READ] Notification {notif_id}")
        
        rpc_server = get_rpc_server()
        result = rpc_server.mark_notification_as_read(user_id,notif_id)
        
        return jsonify(result)
    except Exception as e:
        print(f"[MARK_READ] ❌ Erreur: {e}")
        return jsonify({"success": False})

@patient.route("/dashboard")
def dashboard():
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        print("[AUTH] ❌ Accès refusé au dashboard")
        return redirect("http://localhost:5000/login")
    try:
        # Appel RPC
        rpc_server = get_rpc_server()
        rpc_data = rpc_server.get_dashboard(user_id)
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
    # 🔒 Vérifier authentification
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({'success': False, 'message': 'UNAUTHORIZED'}), 403
    
    try:
        print("="*50)
        print(f"[RDV_DETAILS] Récupération détails pour RDV: {rdv_id}")
        
        # ✅ La vérification de propriété est faite dans le RPC
        rpc_server = get_rpc_server()
        result = rpc_server.get_rendezvous_details(user_id,rdv_id)
        
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
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return redirect("http://localhost:5000/login")

    try:
        print("="*50)
        print(f"[ROUTE] Récupération RDV pour patient_id: {user_id}")
        print("="*50)
        
        # Appel RPC
        rpc_server = get_rpc_server()
        rpc_data = rpc_server.get_all_appointments(user_id)
        
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
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({"success": False, "message": "UNAUTHORIZED"})
    try:
        # Récupérer les données du formulaire
        appointment_id = request.form.get("id")
        medecin_id = request.form.get("medecin_id")
        date = request.form.get("date")
        time_str = request.form.get("time")
        notes = request.form.get("notes", "")
        

        print("="*50)
        print(f"[UPDATE] Mise à jour RDV:")
        print(f"  - ID: {appointment_id}")
        print(f"  - Médecin: {medecin_id}")
        print(f"  - Date: {date}")
        print(f"  - Heure: {time_str}")
        print(f"  - Patient: {user_id}")

        # Validation
        if not (appointment_id and medecin_id and date and time_str):
            return jsonify({
                "success": False, 
                "message": "Tous les champs sont requis."
            })

        # Appel RPC
        rpc_server = get_rpc_server()
        result = rpc_server.update_appointment(
            user_id,
            appointment_id, 
            medecin_id, 
            date, 
            time_str, 
            notes
            
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
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({"success": False, "message": "UNAUTHORIZED"})
    try:
        # Récupérer les données
        data = request.get_json()
        appointment_id = data.get("appointment_id")
        

        print("="*50)
        print(f"[CANCEL] Annulation RDV:")
        print(f"  - RDV ID: {appointment_id}")
        print(f"  - Patient ID: {user_id}")

        # Validation
        if not appointment_id:
            return jsonify({
                "success": False, 
                "message": "ID du rendez-vous manquant"
            })

        # Appel RPC
        rpc_server = get_rpc_server()
        result = rpc_server.cancel_appointment(user_id,appointment_id)
        
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
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return redirect("http://localhost:5000/login")

    try:
        print("="*50)
        print(f"[PROFILE] Appel RPC pour profil patient:")
        print(f"  - Patient ID: {user_id}")

        # Appel RPC
        rpc_server = get_rpc_server()
        rpc_data = rpc_server.get_profile_local(user_id)
        
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
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({"success": False, "message": "UNAUTHORIZED"})
    try:
        # Récupérer les données
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        telephone = request.form.get("telephone", "").strip()
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
        result = rpc_server.update_profile(user_id,nom, email, telephone)
        
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


    return render_template("patient/logout.html")

@patient.route("/prise_rdv")
def prise_rdv():
    return render_template("patient/prise_rdv.html")

@patient.route("/get_doctors")
def get_doctors():
    specialization_id = request.args.get('specialization')

    try:
        print("="*50)
        print(f"[GET_DOCTORS] Récupération médecins:")
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

@patient.route("/get_appointment_review/<int:appointment_id>")
def get_appointment_review(appointment_id):
    """
    Récupère l'avis existant pour un rendez-vous (si existe)
    """
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({"success": False, "message": "UNAUTHORIZED"}), 403
    try:
        
        print(f"[GET_REVIEW] Vérification avis pour RDV {appointment_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer l'ID interne du patient
        cursor.execute("SELECT id FROM patients WHERE user_id = %s", (user_id,))
        patient_row = cursor.fetchone()
        if not patient_row:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Patient introuvable"}), 404
        
        internal_patient_id = patient_row['id']
        
        cursor.execute("""
            SELECT 
                a.id,
                a.note,
                a.commentaire,
                a.date_avis
            FROM avis a
            WHERE a.rendezvous_id = %s AND a.patient_id = %s
        """, (appointment_id, internal_patient_id))
        
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
    Route pour soumettre un avis patient - VERSION CORRIGÉE
    """
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({"success": False, "message": "UNAUTHORIZED"}), 403
    try:
        
        # Récupérer les données JSON
        data = request.get_json()
        
        appointment_id = data.get("appointment_id")
        rating = data.get("rating")
        comment = data.get("comment")
        
        print("="*50)
        print(f"[SUBMIT_REVIEW] Soumission d'avis:")
        print(f"  - Patient User ID: {user_id}")
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
        
        # Récupérer l'ID interne du patient et du médecin depuis le rendez-vous
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # D'abord récupérer l'ID interne du patient
        cursor.execute("SELECT id FROM patients WHERE user_id = %s", (user_id,))
        patient_row = cursor.fetchone()
        if not patient_row:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Patient introuvable"
            }), 404
        
        internal_patient_id = patient_row[0]
        
        # Ensuite récupérer les infos du rendez-vous (avec medecin_id interne)
        cursor.execute("""
            SELECT r.medecin_id, r.statut, m.user_id as medecin_user_id
            FROM rendezvous r
            JOIN medecins m ON r.medecin_id = m.id
            WHERE r.id = %s AND r.patient_id = %s
        """, (appointment_id, internal_patient_id))
        
        rdv_info = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not rdv_info:
            return jsonify({
                "success": False,
                "message": "Rendez-vous introuvable"
            }), 404
        
        internal_medecin_id = rdv_info[0]
        medecin_user_id = rdv_info[2]
        
        print(f"[SUBMIT_REVIEW] IDs trouvés:")
        print(f"  - Internal Patient ID: {internal_patient_id}")
        print(f"  - Internal Medecin ID: {internal_medecin_id}")
        print(f"  - Medecin User ID: {medecin_user_id}")
        
        # Appel RPC pour enregistrer l'avis avec l'ID interne du médecin
        rpc_server = get_rpc_server()
        result = rpc_server.save_patient_review(
            internal_patient_id,
            internal_medecin_id,  # ✅ On passe l'ID interne, pas le user_id
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
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({"success": False, "message": "UNAUTHORIZED"})

    try:
        # Récupérer les données du formulaire
        doctor_id = request.form.get("doctor_id")
        consultation_date = request.form.get("consultation_date")
        consultation_time = request.form.get("consultation_time")
        reason = request.form.get("reason", "")

        print("="*50)
        print(f"[BOOK] Prise de RDV:")
        print(f"  - Patient ID: {user_id}")
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
            user_id,
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
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({"success": False, "message": "UNAUTHORIZED"})
    doctor_id = request.args.get('doctor_id')

    try:
        print("="*50)
        print(f"[GET_HONORAIRES] Récupération honoraires:")
        print(f"  - Patient: {user_id}")
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
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({"success": False, "message": "UNAUTHORIZED"})
    doctor_id = request.args.get("doctor_id")

    try:
        print("="*50)
        print(f"[GET_AVAILABLE_DATES] Récupération dates disponibles:")
        print(f"  - Patient: {user_id}")
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

@patient.route("/get_next_appointment")
def get_next_appointment():
    """
    Retourne le prochain rendez-vous à venir
    """
    user_id, role = get_current_user()
    
    if not user_id or role != "PATIENT":
        return jsonify({
            "success": False,
            "appointment": None
        }), 403
    
    try:
        rpc_server = get_rpc_server()
        result = rpc_server.get_next_appointment(user_id)
        
        if result.get("success") and result.get("appointment"):
            appointment = result["appointment"]
            
            # Formater la date en français (ex: "15 Jan")
            from datetime import datetime
            
            date_str = appointment['date_only']  # Format: 2025-01-15
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Mois en français
            mois_fr = {
                1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr',
                5: 'Mai', 6: 'Juin', 7: 'Juil', 8: 'Août',
                9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc'
            }
            
            date_formatee = f"{date_obj.day} {mois_fr[date_obj.month]}"
            
            return jsonify({
                "success": True,
                "appointment": {
                    "date": date_formatee,  # "15 Jan"
                    "time": appointment['time_only'],  # "10:30"
                    "medecin": appointment['medecin_nom'],
                    "specialite": appointment.get('specialite', '')
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "appointment": None,
                "message": "Aucun rendez-vous à venir"
            }), 200
            
    except Exception as e:
        print(f"[FLASK] ❌ Erreur get_next_appointment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "appointment": None,
            "message": "Erreur serveur"
        }), 500
@patient.route("/change_password", methods=["POST"])
def change_password():
    """
    Change le mot de passe du patient - VERSION CORRIGÉE
    """
    # 🔒 Vérifier authentification avec get_current_user()
    user_id, role = get_current_user()
    
    print(f"[FLASK] 🔍 change_password appelée")
    print(f"[FLASK]   - User ID: {user_id}")
    print(f"[FLASK]   - Rôle: {role}")
    print(f"[FLASK]   - Données reçues: {request.form}")
    
    if not user_id or role != "PATIENT":
        print(f"[FLASK] ❌ Non autorisé")
        return jsonify({
            "success": False,
            "message": "Non autorisé"
        }), 403
    
    try:
        print("="*50)
        print(f"[FLASK] Changement de mot de passe:")
        
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        print(f"[FLASK]   - Current: '{current_password}'")
        print(f"[FLASK]   - New: '{new_password}'")
        print(f"[FLASK]   - Confirm: '{confirm_password}'")
        
        # Validation des champs
        if not all([current_password, new_password, confirm_password]):
            print(f"[FLASK] ❌ Champs manquants")
            return jsonify({
                "success": False,
                "message": "Tous les champs sont requis"
            }), 400
        
        # Vérification correspondance
        if new_password != confirm_password:
            print(f"[FLASK] ❌ Mots de passe différents")
            return jsonify({
                "success": False,
                "message": "Les mots de passe ne correspondent pas"
            }), 400
        
        # Validation longueur
        if len(new_password) < 8:
            print(f"[FLASK] ❌ Mot de passe trop court")
            return jsonify({
                "success": False,
                "message": "Le mot de passe doit contenir au moins 8 caractères"
            }), 400
        
        # Vérifier que le nouveau mot de passe est différent
        if new_password == current_password:
            print(f"[FLASK] ❌ Même mot de passe")
            return jsonify({
                "success": False,
                "message": "Le nouveau mot de passe doit être différent de l'ancien"
            }), 400
        
        # Appeler RPC
        print(f"[FLASK] 📞 Appel RPC...")
        rpc_server = get_rpc_server()
        result = rpc_server.change_password(
            user_id,
            current_password,
            new_password
        )
        
        print(f"[FLASK] ✅ Résultat RPC: {result}")
        print("="*50)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"[FLASK] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erreur serveur"
        }), 500
@patient.route("/logout")
def logout():
    """
    Déconnecte l'utilisateur en supprimant le cookie JWT
    """
    print("[FLASK-LOGOUT] 🔒 Déconnexion en cours...")
    
    user_id, role = get_current_user()
    
    if user_id:
        print(f"[FLASK-LOGOUT] Utilisateur {user_id} ({role}) se déconnecte")
        
        # Optionnel: Appel RPC pour log
        try:
            rpc_server = get_rpc_server()
            rpc_server.logout()
            print("[FLASK-LOGOUT] ✅ RPC appelé avec succès")
        except Exception as e:
            print(f"[FLASK-LOGOUT] ⚠️ RPC non disponible: {e}")
    
    # Créer une réponse de redirection
    response = redirect("http://localhost:5000/login")
    
    # Supprimer le cookie JWT
    response.set_cookie(
        'access_token', 
        '', 
        expires=0,  # Expire immédiatement
        httponly=True,
        secure=False,  # Mettre à True en production avec HTTPS
        samesite='Lax',
        path='/'
    )
    
    # Optionnel: Supprimer d'autres cookies
    response.set_cookie('session', '', expires=0, path='/')
    response.set_cookie('user_id', '', expires=0, path='/')
    
    print("[FLASK-LOGOUT] ✅ Cookies supprimés, redirection vers /login")
    return response