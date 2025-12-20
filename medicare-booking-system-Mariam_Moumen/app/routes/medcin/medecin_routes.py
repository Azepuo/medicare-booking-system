# app/routes/medecin_routes.py

from flask import Blueprint, render_template, jsonify, request, redirect 
from models.patient import Patient
from models.rendezvous import Rendezvous
from models.medecin import Medecin
from database.connection import create_connection
from datetime import date, datetime, timedelta
from models.disponibilite import Disponibilite
import jwt
from app.rpc.auth_rpc.auth_rpc import SECRET_KEY
from models.User import User

medecin = Blueprint('medecin', __name__)



# ------------------ PAGES ------------------
@medecin.route('/dashboard')
def dashboard():
    token = request.cookies.get("access_token")
    if not token:
        return "Utilisateur non connecté", 401

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return "Session expirée, veuillez vous reconnecter", 401
    except jwt.InvalidTokenError:
        return "Token invalide", 401

    user = User.get_by_id(payload["user_id"])

    return render_template(
        "medecin/dashboard.html",
        user_id=payload["user_id"],
        role=payload["role"],
        username=user.nom if user else "Inconnu",
        email=user.email if user else ""
    )

@medecin.route('/patients')
def patients_page():
    return render_template('medecin/patients.html')

@medecin.route('/patients/add')
def patient_add_page():
    return render_template('medecin/patient_add.html')

@medecin.route('/patients/edit/<int:pid>')
def patient_edit_page(pid):
    patient = Patient.get_by_id(pid)
    if not patient:
        return "Patient non trouvé", 404
    return render_template('medecin/patient_edit.html', patient=patient.to_dict())

@medecin.route('/patients/delete/<int:pid>')
def patient_delete_page(pid):
    return render_template('medecin/patient_delete.html', pid=pid)

@medecin.route('/rdv')
def rdv_list():
    return render_template('medecin/rdv_list.html')

@medecin.route('/rdv/add')
def rdv_add_page():
    return render_template('medecin/rdv_add.html')

@medecin.route('/rdv/edit/<int:rid>')
def rdv_edit_page(rid):
    return render_template('medecin/rdv_edit.html', rid=rid)

@medecin.route('/rdv/delete/<int:rid>')
def rdv_delete_page(rid):
    return render_template('medecin/rdv_delete.html', rid=rid)

@medecin.route('/disponibilites')
def dispo_list():
    return render_template('medecin/disponibilites.html')

@medecin.route('/disponibilites/add')
def dispo_add():
    return render_template('medecin/disponibilites_add.html')

@medecin.route("/disponibilites/edit/<int:dispo_id>")
def dispo_edit(dispo_id):
    return render_template(
        "medecin/disponibilites_edit.html",
        dispo_id=dispo_id
    )

@medecin.route('/chat')
def chat():
    return render_template('medecin/chat.html')

# routes/medcin/medecin_routes.py

# ------------------ PAGES ------------------
@medecin.route('/profil')
def profil():
    token = request.cookies.get("access_token")
    if not token:
        return redirect('/login')

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return "Session expirée, veuillez vous reconnecter", 401
    except jwt.InvalidTokenError:
        return "Token invalide", 401

    user_id = payload["user_id"]
    
    # Utiliser User.get_by_id pour récupérer les données de base
    user = User.get_by_id(user_id)
    
    if not user:
        return "Utilisateur non trouvé", 404
    
    # Si User a un attribut created_at, l'utiliser, sinon utiliser une valeur par défaut
    # Vérifier d'abord si l'attribut existe
    date_inscription = ''
    if hasattr(user, 'created_at') and user.created_at:
        # Vérifier le type
        if isinstance(user.created_at, datetime):
            date_inscription = user.created_at.strftime('%d/%m/%Y')
        else:
            date_inscription = str(user.created_at)
    else:
        # Valeur par défaut ou récupérer depuis la base
        date_inscription = "Non disponible"
    
    # Récupérer le nom d'utilisateur depuis l'email
    username = ""
    if hasattr(user, 'email') and user.email:
        username = user.email.split('@')[0]
    
    # Créer un objet user avec les champs disponibles
    user_data = {
        'nom_complet': user.nom if hasattr(user, 'nom') and user.nom else '',
        'email': user.email if hasattr(user, 'email') and user.email else '',
        'telephone': user.telephone if hasattr(user, 'telephone') and user.telephone else '',
        'role': payload.get('role', ''),
        'user_id': user_id,
        'date_inscription': date_inscription,
        
        # Champs par défaut (vides ou valeurs par défaut)
        'specialite': '',
        'tarif': 0,
        'titre': '',
        'adresse': '',
        'ville': '',
        'code_postal': '',
        'rpps': '',
        'experience': 0,
        'langues': '',
        'diplomes': '',
        'horaires': '',
        'biographie': '',
        'paiement_carte': False,
        'paiement_cheque': False,
        'paiement_especes': False,
        'paiement_tiers': False,
        'specialites': '',
        'username': username
    }
    
    return render_template('medecin/profil.html', user=user_data)
# ------------------ HELPERS ------------------
def verify_token(required_role="MEDECIN"):
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        return None, jsonify({'ok': False, 'error': 'Non authentifié'}), 401

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None, jsonify({'ok': False, 'error': 'Session expirée'}), 401
    except jwt.InvalidTokenError:
        return None, jsonify({'ok': False, 'error': 'Token invalide'}), 401

    role = payload.get("role", "").upper()
    if role != required_role.upper():
        return None, jsonify({'ok': False, 'error': f'Accès non autorisé. Rôle requis: {required_role}'}), 403

    return payload, None, None

# ------------------ RPC ROUTES POUR PROFIL ------------------
@medecin.route('/api/profile', methods=['GET'])
def get_profile_api():
    """API pour récupérer les données du profil (AJAX)"""
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status
    
    try:
        user_id = payload["user_id"]
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        return jsonify({
            'nom_complet': user.nom if user.nom else '',
            'email': user.email if user.email else '',
            'telephone': user.telephone if user.telephone else '',
            'role': payload.get('role', ''),
            'date_inscription': user.created_at.strftime('%d/%m/%Y') if user.created_at else ''
        })
    except Exception as e:
        print(f"❌ Erreur get_profile_api: {e}")
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/profile', methods=['PUT'])
def update_profile_api():
    """API pour mettre à jour le profil"""
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status
    
    data = request.json
    if not data:
        return jsonify({'error': 'Données manquantes'}), 400
    
    try:
        user_id = payload["user_id"]
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Mettre à jour les informations de base
        update_data = {}
        
        if 'nom_complet' in data:
            update_data['nom'] = data['nom_complet']
        if 'email' in data:
            update_data['email'] = data['email']
        if 'telephone' in data:
            update_data['telephone'] = data['telephone']
        if 'adresse' in data:
            update_data['adresse'] = data['adresse']
        
        # Mettre à jour le mot de passe si fourni
        if data.get('password'):
            from werkzeug.security import generate_password_hash
            update_data['password'] = generate_password_hash(data.get('password'))
        
        # Utiliser la méthode save du modèle User si elle existe
        if hasattr(user, 'save'):
            for key, value in update_data.items():
                setattr(user, key, value)
            user.save()
        else:
            # Sinon, utiliser une connexion directe
            conn = create_connection()
            if not conn:
                return jsonify({'error': 'Erreur de connexion à la base'}), 500
            
            cursor = conn.cursor()
            
            # Construire la requête SQL
            if update_data:
                set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
                query = f"UPDATE users SET {set_clause} WHERE id = %s"
                values = list(update_data.values()) + [user_id]
                
                cursor.execute(query, values)
                conn.commit()
            
            cursor.close()
            conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Profil mis à jour avec succès'
        })
        
    except Exception as e:
        print(f"❌ Erreur update_profile_api: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ------------------ RPC ROUTES POUR RDV ------------------
@medecin.route('/rpc/rdv/list', methods=['GET'])
def list_rdv_rpc():
    """Lister les rendez-vous (avec paramètre today=1 pour aujourd'hui seulement)"""
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status
    
    try:
        # Vérifier si c'est pour aujourd'hui seulement
        today_only = request.args.get('today') == '1'
        
        user_id = payload["user_id"]
        
        conn = create_connection()
        if not conn:
            return jsonify({'ok': False, 'error': 'Erreur de connexion à la base'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        if today_only:
            # CORRECTION CRITIQUE: Rendez-vous d'aujourd'hui seulement
            # On utilise DATE() pour extraire la partie date du DATETIME
            cursor.execute("""
                SELECT 
                    r.*,
                    p.nom as patient_nom,
                    p.telephone as patient_telephone,
                    p.email as patient_email
                FROM rendezvous r
                LEFT JOIN patients p ON r.patient_id = p.id
                WHERE r.user_id = %s 
                AND DATE(r.date_heure) = CURDATE()
                ORDER BY r.date_heure ASC
            """, (user_id,))
        else:
            # Tous les rendez-vous (pour d'autres vues)
            cursor.execute("""
                SELECT 
                    r.*,
                    p.nom as patient_nom,
                    p.telephone as patient_telephone,
                    p.email as patient_email
                FROM rendezvous r
                LEFT JOIN patients p ON r.patient_id = p.id
                WHERE r.user_id = %s
                ORDER BY r.date_heure DESC
            """, (user_id,))
        
        rdvs = cursor.fetchall()
        
        print(f"DEBUG: RDV trouvés: {len(rdvs)}")
        for rdv in rdvs:
            print(f"DEBUG: RDV id={rdv['id']}, date={rdv['date_heure']}, statut={rdv.get('statut')}")
        
        # Formater les dates pour JSON
        for rdv in rdvs:
            if 'date_heure' in rdv and rdv['date_heure']:
                if isinstance(rdv['date_heure'], str):
                    # Déjà un string, vérifier le format
                    try:
                        dt = datetime.fromisoformat(rdv['date_heure'].replace('Z', '+00:00'))
                        rdv['date_heure'] = dt.isoformat()
                    except:
                        pass
                else:
                    # Objet datetime MySQL
                    rdv['date_heure'] = rdv['date_heure'].isoformat()
        
        cursor.close()
        conn.close()
        
        return jsonify({'ok': True, 'data': rdvs})
        
    except Exception as e:
        print(f"❌ Erreur list_rdv_rpc: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500

# ------------------ NOUVELLE ROUTE POUR RDV FUTURS ------------------
@medecin.route('/rpc/rdv/list/future', methods=['GET'])
def list_future_rdv_rpc():
    """Lister les rendez-vous futurs (aujourd'hui et après)"""
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status
    
    try:
        user_id = payload["user_id"]
        
        conn = create_connection()
        if not conn:
            return jsonify({'ok': False, 'error': 'Erreur de connexion à la base'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Rendez-vous à partir d'aujourd'hui (futurs)
        cursor.execute("""
            SELECT 
                r.*,
                p.nom as patient_nom,
                p.telephone as patient_telephone,
                p.email as patient_email
            FROM rendezvous r
            LEFT JOIN patients p ON r.patient_id = p.id
            WHERE r.user_id = %s 
            AND DATE(r.date_heure) >= CURDATE()
            ORDER BY r.date_heure ASC
        """, (user_id,))
        
        rdvs = cursor.fetchall()
        
        # Formater les dates pour JSON
        for rdv in rdvs:
            if 'date_heure' in rdv and rdv['date_heure']:
                if isinstance(rdv['date_heure'], str):
                    try:
                        dt = datetime.fromisoformat(rdv['date_heure'].replace('Z', '+00:00'))
                        rdv['date_heure'] = dt.isoformat()
                    except:
                        pass
                else:
                    rdv['date_heure'] = rdv['date_heure'].isoformat()
        
        cursor.close()
        conn.close()
        
        return jsonify({'ok': True, 'data': rdvs})
        
    except Exception as e:
        print(f"❌ Erreur list_future_rdv_rpc: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500

@medecin.route('/rpc/rdv/create', methods=['POST'])
def create_rdv_rpc():
    """Créer un nouveau rendez-vous"""
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status

    data = request.get_json()
    if not data or 'patient_id' not in data or 'date_heure' not in data:
        return jsonify({'ok': False, 'error': 'Champs patient_id et date_heure requis'}), 400

    try:
        user_id = payload["user_id"]
        
        # Vérifier que le patient existe
        patient = Patient.get_by_id(data['patient_id'])
        if not patient:
            return jsonify({'ok': False, 'error': 'Patient non trouvé'}), 404
        
        # Vérifier que l'utilisateur est bien un médecin
        medecin_user = Medecin.get_by_user_id(user_id)
        if not medecin_user:
            return jsonify({'ok': False, 'error': 'Médecin non trouvé'}), 404
        
        # CORRECTION: Formater correctement la date pour MySQL
        date_heure = data['date_heure']
        # Si la date contient 'T', la remplacer par un espace pour MySQL
        if 'T' in date_heure:
            date_heure = date_heure.replace('T', ' ')
        # Supprimer le 'Z' si présent
        if date_heure.endswith('Z'):
            date_heure = date_heure[:-1]
        
        print(f"DEBUG: Création RDV - user_id={user_id}, date_heure={date_heure}")
        
        # Insérer le rendez-vous
        conn = create_connection()
        if not conn:
            return jsonify({'ok': False, 'error': 'Erreur de connexion à la base'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Utiliser user_id directement (comme vous le voulez)
        cursor.execute("""
            INSERT INTO rendezvous 
            (date_heure, patient_id, user_id, statut, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            date_heure,
            data['patient_id'],
            user_id,  # user_id du médecin
            data.get('statut', 'En attente'),
            data.get('notes', '')
        ))
        
        conn.commit()
        rdv_id = cursor.lastrowid
        
        # Vérifier que le RDV a été inséré
        cursor.execute("SELECT * FROM rendezvous WHERE id = %s", (rdv_id,))
        rdv_inserted = cursor.fetchone()
        print(f"DEBUG: RDV inséré - {rdv_inserted}")
        
        cursor.close()
        conn.close()
        
        return jsonify({'ok': True, 'id': rdv_id, 'message': 'Rendez-vous créé avec succès'})
        
    except Exception as e:
        print(f"❌ Erreur create_rdv_rpc: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500

@medecin.route('/rpc/rdv/update/<int:rdv_id>', methods=['POST'])
def update_rdv_rpc(rdv_id):
    """Mettre à jour un rendez-vous"""
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status

    data = request.get_json()
    if not data:
        return jsonify({'ok': False, 'error': 'Données JSON requises'}), 400

    try:
        user_id = payload["user_id"]
        
        conn = create_connection()
        if not conn:
            return jsonify({'ok': False, 'error': 'Erreur de connexion à la base'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Vérifier que le RDV appartient au médecin
        cursor.execute("""
            SELECT * FROM rendezvous 
            WHERE id = %s AND user_id = %s
        """, (rdv_id, user_id))
        
        rdv = cursor.fetchone()
        if not rdv:
            cursor.close()
            conn.close()
            return jsonify({'ok': False, 'error': 'Rendez-vous non trouvé ou accès non autorisé'}), 404
        
        # Mettre à jour
        cursor.execute("""
            UPDATE rendezvous
            SET date_heure = %s, statut = %s, notes = %s
            WHERE id = %s
        """, (
            data.get('date_heure', rdv['date_heure']),
            data.get('statut', rdv['statut']),
            data.get('notes', rdv['notes']),
            rdv_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'ok': True, 'message': 'Rendez-vous mis à jour avec succès'})
        
    except Exception as e:
        print(f"❌ Erreur update_rdv_rpc: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@medecin.route('/rpc/rdv/delete/<int:rdv_id>', methods=['DELETE'])
def delete_rdv_rpc(rdv_id):
    """Supprimer un rendez-vous"""
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status

    try:
        user_id = payload["user_id"]
        
        conn = create_connection()
        if not conn:
            return jsonify({'ok': False, 'error': 'Erreur de connexion à la base'}), 500
        
        cursor = conn.cursor()
        
        # Vérifier que le RDV appartient au médecin
        cursor.execute("""
            SELECT id FROM rendezvous 
            WHERE id = %s AND user_id = %s
        """, (rdv_id, user_id))
        
        rdv = cursor.fetchone()
        if not rdv:
            cursor.close()
            conn.close()
            return jsonify({'ok': False, 'error': 'Rendez-vous non trouvé ou accès non autorisé'}), 404
        
        # Supprimer le RDV
        cursor.execute("DELETE FROM rendezvous WHERE id = %s", (rdv_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'ok': True, 'message': 'Rendez-vous supprimé avec succès'})
        
    except Exception as e:
        print(f"❌ Erreur delete_rdv_rpc: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

# ------------------ RPC ROUTES POUR DISPONIBILITES ------------------
@medecin.route('/rpc/disponibilites/list', methods=['GET'])
def list_dispo_rpc():
    """Lister les disponibilités (avec paramètre today=1 pour aujourd'hui)"""
    print("DEBUG: Début list_dispo_rpc")
    payload, err_response, status = verify_token()
    if err_response:
        print(f"DEBUG: Erreur token: {err_response}")
        return err_response, status
    
    try:
        # Vérifier si c'est pour aujourd'hui seulement
        today_only = request.args.get('today') == '1'
        user_id = payload["user_id"]
        print(f"DEBUG: user_id={user_id}, today_only={today_only}")
        
        # Jour de la semaine en français pour today
        jours_fr = {
            'Monday': 'Lundi',
            'Tuesday': 'Mardi',
            'Wednesday': 'Mercredi',
            'Thursday': 'Jeudi',
            'Friday': 'Vendredi',
            'Saturday': 'Samedi',
            'Sunday': 'Dimanche'
        }
        jour_aujourdhui = jours_fr.get(datetime.now().strftime('%A'))
        print(f"DEBUG: Jour aujourd'hui: {jour_aujourdhui}")
        
        conn = create_connection()
        if not conn:
            print("DEBUG: Erreur de connexion à la base")
            return jsonify({'ok': False, 'error': 'Erreur de connexion à la base'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        if today_only and jour_aujourdhui:
            # Disponibilités pour aujourd'hui seulement
            print(f"DEBUG: Recherche disponibilités pour {jour_aujourdhui}")
            cursor.execute("""
                SELECT * FROM disponibilites 
                WHERE user_id = %s AND jour_semaine = %s
                ORDER BY heure_debut
            """, (user_id, jour_aujourdhui))
        else:
            # Toutes les disponibilités
            print("DEBUG: Recherche toutes les disponibilités")
            cursor.execute("""
                SELECT * FROM disponibilites 
                WHERE user_id = %s
                ORDER BY 
                    FIELD(jour_semaine, 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'),
                    heure_debut
            """, (user_id,))
        
        disponibilites = cursor.fetchall()
        print(f"DEBUG: Disponibilités trouvées: {len(disponibilites)}")
        
        # CORRECTION CRITIQUE: Convertir les objets timedelta en strings
        for dispo in disponibilites:
            # Convertir les champs TIME (timedelta) en strings
            if 'heure_debut' in dispo and dispo['heure_debut']:
                if isinstance(dispo['heure_debut'], timedelta):
                    # Convertir timedelta en string HH:MM:SS
                    total_seconds = int(dispo['heure_debut'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    dispo['heure_debut'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                elif not isinstance(dispo['heure_debut'], str):
                    dispo['heure_debut'] = str(dispo['heure_debut'])
            
            if 'heure_fin' in dispo and dispo['heure_fin']:
                if isinstance(dispo['heure_fin'], timedelta):
                    # Convertir timedelta en string HH:MM:SS
                    total_seconds = int(dispo['heure_fin'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    dispo['heure_fin'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                elif not isinstance(dispo['heure_fin'], str):
                    dispo['heure_fin'] = str(dispo['heure_fin'])
            
            # Format simplifié pour le template
            if isinstance(dispo.get('heure_debut'), str) and ':' in dispo['heure_debut']:
                dispo['heure_debut_display'] = dispo['heure_debut'][:5]  # Garder seulement HH:MM
            if isinstance(dispo.get('heure_fin'), str) and ':' in dispo['heure_fin']:
                dispo['heure_fin_display'] = dispo['heure_fin'][:5]  # Garder seulement HH:MM
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'ok': True, 
            'data': disponibilites, 
            'today': jour_aujourdhui if today_only else None
        })
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE list_dispo_rpc: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'ok': False, 'error': f'Erreur serveur: {str(e)}'}), 500
    
@medecin.route('/rpc/disponibilites/create', methods=['POST'])
def create_dispo_rpc():
    """Créer une nouvelle disponibilité"""
    print("DEBUG: Début create_dispo_rpc")
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status

    data = request.get_json()
    print(f"DEBUG: Données reçues: {data}")
    
    if not data or 'jour_semaine' not in data or 'heure_debut' not in data or 'heure_fin' not in data:
        return jsonify({'ok': False, 'error': 'Champs jour_semaine, heure_debut et heure_fin requis'}), 400

    try:
        user_id = payload["user_id"]
        
        # Vérifier les heures
        if data['heure_debut'] >= data['heure_fin']:
            return jsonify({'ok': False, 'error': 'L\'heure de début doit être avant l\'heure de fin'}), 400
        
        conn = create_connection()
        if not conn:
            return jsonify({'ok': False, 'error': 'Erreur de connexion à la base'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Vérifier d'abord si la table existe
        cursor.execute("SHOW TABLES LIKE 'disponibilites'")
        table_exists = cursor.fetchone()
        if not table_exists:
            print("DEBUG: Table disponibilites n'existe pas, création...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS disponibilites (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    jour_semaine VARCHAR(20) NOT NULL,
                    heure_debut TIME NOT NULL,
                    heure_fin TIME NOT NULL,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_id (user_id),
                    INDEX idx_jour (jour_semaine)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            conn.commit()
        
        # Vérifier les conflits
        cursor.execute("""
            SELECT * FROM disponibilites 
            WHERE user_id = %s AND jour_semaine = %s 
            AND (
                (heure_debut <= %s AND heure_fin > %s) OR
                (heure_debut < %s AND heure_fin >= %s) OR
                (heure_debut >= %s AND heure_fin <= %s)
            )
        """, (
            user_id, data['jour_semaine'],
            data['heure_debut'], data['heure_debut'],
            data['heure_fin'], data['heure_fin'],
            data['heure_debut'], data['heure_fin']
        ))
        
        existing = cursor.fetchone()
        if existing:
            cursor.close()
            conn.close()
            return jsonify({'ok': False, 'error': 'Une disponibilité existe déjà pour cette plage horaire'}), 409
        
        # Insérer la disponibilité
        cursor.execute("""
            INSERT INTO disponibilites (user_id, jour_semaine, heure_debut, heure_fin)
            VALUES (%s, %s, %s, %s)
        """, (user_id, data['jour_semaine'], data['heure_debut'], data['heure_fin']))
        
        conn.commit()
        dispo_id = cursor.lastrowid
        
        # Récupérer la disponibilité créée pour la retourner
        cursor.execute("SELECT * FROM disponibilites WHERE id = %s", (dispo_id,))
        new_dispo = cursor.fetchone()
        
        # Convertir les timedelta en strings
        if new_dispo:
            if 'heure_debut' in new_dispo and isinstance(new_dispo['heure_debut'], timedelta):
                total_seconds = int(new_dispo['heure_debut'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                new_dispo['heure_debut'] = f"{hours:02d}:{minutes:02d}:00"
            
            if 'heure_fin' in new_dispo and isinstance(new_dispo['heure_fin'], timedelta):
                total_seconds = int(new_dispo['heure_fin'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                new_dispo['heure_fin'] = f"{hours:02d}:{minutes:02d}:00"
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'ok': True, 
            'id': dispo_id, 
            'data': new_dispo,
            'message': 'Disponibilité créée avec succès'
        })
        
    except Exception as e:
        print(f"❌ Erreur create_dispo_rpc: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'ok': False, 'error': f'Erreur: {str(e)}'}), 500
    
@medecin.route('/rpc/disponibilites/update/<int:dispo_id>', methods=['POST'])
def update_dispo_rpc(dispo_id):
    """Mettre à jour une disponibilité"""
    print(f"DEBUG: Début update_dispo_rpc pour id={dispo_id}")
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status

    data = request.get_json()
    if not data:
        return jsonify({'ok': False, 'error': 'Données JSON requises'}), 400

    try:
        user_id = payload["user_id"]
        
        # Vérifier les heures
        if 'heure_debut' in data and 'heure_fin' in data:
            if data['heure_debut'] >= data['heure_fin']:
                return jsonify({'ok': False, 'error': 'L\'heure de début doit être avant l\'heure de fin'}), 400
        
        conn = create_connection()
        if not conn:
            return jsonify({'ok': False, 'error': 'Erreur de connexion à la base'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Vérifier que la disponibilité appartient à l'utilisateur
        cursor.execute("""
            SELECT * FROM disponibilites 
            WHERE id = %s AND user_id = %s
        """, (dispo_id, user_id))
        
        dispo = cursor.fetchone()
        if not dispo:
            cursor.close()
            conn.close()
            return jsonify({'ok': False, 'error': 'Disponibilité non trouvée ou accès non autorisé'}), 404
        
        # Vérifier les conflits (sauf avec elle-même)
        if 'jour_semaine' in data or 'heure_debut' in data or 'heure_fin' in data:
            jour = data.get('jour_semaine', dispo['jour_semaine'])
            debut = data.get('heure_debut', dispo['heure_debut'])
            fin = data.get('heure_fin', dispo['heure_fin'])
            
            cursor.execute("""
                SELECT * FROM disponibilites 
                WHERE user_id = %s AND jour_semaine = %s 
                AND id != %s
                AND (
                    (heure_debut <= %s AND heure_fin > %s) OR
                    (heure_debut < %s AND heure_fin >= %s) OR
                    (heure_debut >= %s AND heure_fin <= %s)
                )
            """, (
                user_id, jour, dispo_id,
                debut, debut,
                fin, fin,
                debut, fin
            ))
            
            existing = cursor.fetchone()
            if existing:
                cursor.close()
                conn.close()
                return jsonify({'ok': False, 'error': 'Une disponibilité existe déjà pour cette plage horaire'}), 409
        
        # Mettre à jour
        cursor.execute("""
            UPDATE disponibilites
            SET jour_semaine = %s, heure_debut = %s, heure_fin = %s
            WHERE id = %s AND user_id = %s
        """, (
            data.get('jour_semaine', dispo['jour_semaine']),
            data.get('heure_debut', dispo['heure_debut']),
            data.get('heure_fin', dispo['heure_fin']),
            dispo_id,
            user_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'ok': True, 'message': 'Disponibilité mise à jour avec succès'})
        
    except Exception as e:
        print(f"❌ Erreur update_dispo_rpc: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@medecin.route('/rpc/disponibilites/delete/<int:dispo_id>', methods=['DELETE'])
def delete_dispo_rpc(dispo_id):
    """Supprimer une disponibilité"""
    print(f"DEBUG: Début delete_dispo_rpc pour id={dispo_id}")
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status

    try:
        user_id = payload["user_id"]
        
        conn = create_connection()
        if not conn:
            return jsonify({'ok': False, 'error': 'Erreur de connexion à la base'}), 500
        
        cursor = conn.cursor()
        
        # Vérifier que la disponibilité appartient à l'utilisateur
        cursor.execute("""
            SELECT id FROM disponibilites 
            WHERE id = %s AND user_id = %s
        """, (dispo_id, user_id))
        
        dispo = cursor.fetchone()
        if not dispo:
            cursor.close()
            conn.close()
            return jsonify({'ok': False, 'error': 'Disponibilité non trouvée ou accès non autorisé'}), 404
        
        # Supprimer la disponibilité
        cursor.execute("DELETE FROM disponibilites WHERE id = %s", (dispo_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'ok': True, 'message': 'Disponibilité supprimée avec succès'})
        
    except Exception as e:
        print(f"❌ Erreur delete_dispo_rpc: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

# ------------------ API PATIENTS ------------------
@medecin.route('/api/patients', methods=['GET'])
def get_patients_api():
    """API pour charger la liste des patients dans les formulaires"""
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status
    
    try:
        patients = Patient.get_all()
        # Retourner uniquement les champs nécessaires
        patients_data = []
        for p in patients:
            patients_data.append({
                'id': p.id,
                'nom': p.nom,
                'email': p.email,
                'telephone': p.telephone or ''
            })
        return jsonify(patients_data)
    except Exception as e:
        print(f"❌ Erreur get_patients_api: {e}")
        return jsonify([]), 200  # Retourner une liste vide plutôt qu'une erreur

@medecin.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient_api(patient_id):
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status
        
    try:
        p = Patient.get_by_id(patient_id)
        if not p:
            return jsonify({'error': 'Patient non trouvé'}), 404
        return jsonify(p.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/patients', methods=['POST'])
def create_patient_api():
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status
        
    try:
        data = request.json
        if not data or not data.get('nom') or not data.get('email'):
            return jsonify({'error': 'Nom et email obligatoires'}), 400

        patient = Patient(
            user_id=data.get('user_id'),
            nom=data['nom'],
            email=data['email'],
            telephone=data.get('telephone', ''),
            sexe=data.get('sexe', 'Homme')
        )
        if patient.save():
            return jsonify({'message': 'Patient créé avec succès', 'id': patient.id}), 201
        return jsonify({'error': 'Erreur lors de la création du patient'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient_api(patient_id):
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status
        
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400

        patient = Patient.get_by_id(patient_id)
        if not patient:
            return jsonify({'error': 'Patient non trouvé'}), 404

        patient.nom = data.get('nom', patient.nom)
        patient.email = data.get('email', patient.email)
        patient.telephone = data.get('telephone', patient.telephone)
        patient.sexe = data.get('sexe', patient.sexe)

        if patient.save():
            return jsonify({'message': 'Patient mis à jour avec succès'})
        return jsonify({'error': 'Erreur mise à jour'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medecin.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient_api(patient_id):
    payload, err_response, status = verify_token()
    if err_response:
        return err_response, status
        
    try:
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return jsonify({'error': 'Patient non trouvé'}), 404

        if patient.delete():
            return jsonify({'message': 'Patient supprimé avec succès'})
        return jsonify({'error': 'Erreur suppression'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500