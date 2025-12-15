from xmlrpc.server import SimpleXMLRPCServer
from database.connection import create_connection
from decimal import Decimal
from datetime import timedelta
import bcrypt
import datetime
from datetime import date

import secrets
import string

def generate_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

# =====================================================
# ✅ liste SPECIALISATIONS
# =====================================================
def liste_specialisations():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, nom FROM specialisations ORDER BY nom")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

# =====================================================
# ✅ NORMALISATION MEDECINS
# =====================================================

def normalize_medecin(row):
    if row is None:
        return None

    data = dict(row)

    for k, v in data.items():
        if isinstance(v, Decimal):
            data[k] = float(v)

    if data.get("date_inscription"):
        data["date_inscription"] = data["date_inscription"].isoformat()

    return data


# =====================================================
# ✅ FONCTIONS MEDECINS
# =====================================================

def liste_medecins(search=""):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT
            m.id,
            u.nom,
            u.email,
            u.telephone,
            u.created_at AS date_inscription,
            s.nom AS specialisation,
            m.tarif_consultation,
            m.statut
        FROM medecins m
        JOIN users u ON m.user_id = u.id
        LEFT JOIN specialisations s ON m.id_specialisation = s.id
    """

    params = ()

    if search:
        sql += """
            WHERE u.nom LIKE %s
               OR u.email LIKE %s
               OR u.telephone LIKE %s
               OR s.nom LIKE %s
        """
        params = (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [normalize_medecin(r) for r in rows]


def get_medecin(medecin_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            m.id,
            u.nom,
            u.email,
            u.telephone,
            u.created_at AS date_inscription,
            m.id_specialisation,
            s.nom AS specialisation,
            m.tarif_consultation,
            m.statut
        FROM medecins m
        JOIN users u ON m.user_id = u.id
        LEFT JOIN specialisations s ON m.id_specialisation = s.id
        WHERE m.id = %s
    """, (medecin_id,))

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return normalize_medecin(row)


def ajouter_medecin(data):
    if not data.get("nom_complet") or not data.get("email"):
        raise Exception("DONNEES_INCOMPLETES")

    conn = create_connection()
    cursor = conn.cursor()

    # 🔐 mot de passe généré
    plain_password = generate_password()
    hashed_password = bcrypt.hashpw(
        plain_password.encode(),
        bcrypt.gensalt()
    ).decode()

    # 1️⃣ USER (authentification)
    cursor.execute("""
        INSERT INTO users (nom, email, telephone, password, role)
        VALUES (%s, %s, %s, %s, 'MEDECIN')
    """, (
        data["nom_complet"],
        data["email"],
        data.get("telephone"),
        hashed_password
    ))

    user_id = cursor.lastrowid

    # 2️⃣ MEDECIN (profil)
    cursor.execute("""
        INSERT INTO medecins (
            user_id,
            nom,
            email,
            telephone,
            id_specialisation,
            tarif_consultation,
            statut
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        data["nom_complet"],
        data["email"],
        data.get("telephone"),
        data.get("id_specialisation"),
        data.get("tarif_consultation"),
        data.get("statut", "Actif")
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "generated_password": plain_password
    }


def editer_medecin(medecin_id, data):
    conn = create_connection()
    cursor = conn.cursor()

    # récupérer user_id
    cursor.execute("SELECT user_id FROM medecins WHERE id = %s", (medecin_id,))
    user_id = cursor.fetchone()[0]

    # update users
    cursor.execute("""
        UPDATE users
        SET nom=%s, email=%s, telephone=%s
        WHERE id=%s
    """, (
        data.get("nom"),
        data.get("email"),
        data.get("telephone"),
        user_id
    ))

    # update medecins
    cursor.execute("""
        UPDATE medecins
        SET id_specialisation=%s,
            tarif_consultation=%s,
            statut=%s
        WHERE id=%s
    """, (
        data.get("id_specialisation"),
        data.get("tarif_consultation"),
        data.get("statut"),
        medecin_id
    ))

    conn.commit()
    cursor.close()
    conn.close()
    return True


def supprimer_medecin(medecin_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM medecins WHERE id = %s", (medecin_id,))
    user_id = cursor.fetchone()[0]

    cursor.execute("DELETE FROM medecins WHERE id = %s", (medecin_id,))
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

    conn.commit()
    cursor.close()
    conn.close()
    return True




# =====================================================
# ✅ NORMALISATION PATIENTS
# =====================================================

def normalize_patient(row):
    if row is None:
        return None

    data = dict(row)

    if data.get("date_naissance"):
        data["date_naissance"] = data["date_naissance"].isoformat()

    if data.get("date_inscription"):
        data["date_inscription"] = data["date_inscription"].isoformat()

    return data


# =====================================================
# ✅ FONCTIONS PATIENTS
# =====================================================

def liste_patients(search=""):
    try:
        conn = create_connection()
        if not conn:
            print("Erreur: Connexion BD impossible")
            return []
        
        cursor = conn.cursor(dictionary=True)

        if search:
            cursor.execute("""
                SELECT * FROM patients
                WHERE nom LIKE %s
                   OR email LIKE %s
                   OR telephone LIKE %s
                   OR cin LIKE %s
            """, (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("SELECT * FROM patients")

        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [normalize_patient(row) for row in rows]
    except Exception as e:
        print(f"Erreur liste_patients: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_patient(patient_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return normalize_patient(row)


def ajouter_patient(data):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients
        (nom, cin, email, telephone, sexe, date_naissance)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data.get("nom"),
        data.get("cin"),
        data.get("email"),
        data.get("telephone"),
        data.get("sexe"),
        data.get("date_naissance"),
    ))

    conn.commit()
    cursor.close()
    conn.close()
    return True


def editer_patient(patient_id, data):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE patients
        SET nom=%s, cin=%s, email=%s, telephone=%s, sexe=%s,
            date_naissance=%s
        WHERE id=%s
    """, (
        data.get("nom"),
        data.get("cin"),
        data.get("email"),
        data.get("telephone"),
        data.get("sexe"),
        data.get("date_naissance"),
        patient_id
    ))

    conn.commit()
    cursor.close()
    conn.close()
    return True


def supprimer_patient(patient_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return True


# =====================================================
# ✅ NORMALISATION RDV
# =====================================================
def normalize_rdv(row):
    if row is None:
        return None

    data = dict(row)

    if data.get("date_rdv"):
        data["date_rdv"] = str(data["date_rdv"])

    # ⚠ ajouter ceci si tu veux être sûre
    if "tarif_consultation" in data:
        data["tarif_consultation"] = float(data["tarif_consultation"])
    
    heure = data.get("heure_rdv")
    if heure is not None:
        if isinstance(heure, timedelta):
            total_seconds = int(heure.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            data["heure_rdv"] = f"{hours:02d}:{minutes:02d}"
        elif hasattr(heure, "strftime"):
            data["heure_rdv"] = heure.strftime("%H:%M")
        else:
            data["heure_rdv"] = str(heure)

    return data


# =====================================================
# ✅ FONCTIONS RDV
# =====================================================

def liste_rdv(search=""):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        cursor.execute("""
            SELECT r.*,
                   p.nom AS patient_nom,
                   m.nom AS medecin_nom
            FROM rendezvous r
            JOIN patients p ON r.patient_id = p.id
            JOIN medecins m ON r.medecin_id = m.id
            WHERE p.nom LIKE %s
               OR m.nom LIKE %s
               OR r.statut LIKE %s
            ORDER BY r.date_rdv DESC, r.heure_rdv ASC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))
    else:
        cursor.execute("""
            SELECT r.*,
                   p.nom AS patient_nom,
                   m.nom AS medecin_nom
            FROM rendezvous r
            JOIN patients p ON r.patient_id = p.id
            JOIN medecins m ON r.medecin_id = m.id
            ORDER BY r.date_rdv DESC, r.heure_rdv ASC
        """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [normalize_rdv(row) for row in rows]


def get_rdv(rdv_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.*,
               p.nom AS patient_nom,
               m.nom AS medecin_nom,
               m.tarif_consultation
        FROM rendezvous r
        JOIN patients p ON r.patient_id = p.id
        JOIN medecins m ON r.medecin_id = m.id
        WHERE r.id = %s
    """, (rdv_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return normalize_rdv(row)


# ✅ Fonction interne de vérification
def rdv_is_valid(data, ignore_id=None):
    """Retourne: 'OK', 'INACTIVE', 'NOT_AVAILABLE', 'ALREADY_BOOKED'"""

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ 0) Vérifier statut du médecin
    cursor.execute("""
        SELECT statut FROM medecins WHERE id = %s
    """, (data.get("medecin_id"),))

    med = cursor.fetchone()

    if not med or med["statut"] != "Actif":
        cursor.close()
        conn.close()
        return "INACTIVE"

    # ✅ 1) Vérifier disponibilité
    cursor.execute("""
        SELECT * FROM disponibilites_medecin
        WHERE medecin_id = %s
        AND date_disponible = %s
        AND %s BETWEEN heure_debut AND heure_fin
    """, (
        data.get("medecin_id"),
        data.get("date_rdv"),
        data.get("heure_rdv")
    ))

    dispo = cursor.fetchone()
    if not dispo:
        cursor.close()
        conn.close()
        return "NOT_AVAILABLE"

    # ✅ 2) Vérifier conflits
    sql_conflict = """
        SELECT * FROM rendezvous
        WHERE medecin_id = %s
        AND date_rdv = %s
        AND heure_rdv = %s
    """
    params = [
        data.get("medecin_id"),
        data.get("date_rdv"),
        data.get("heure_rdv")
    ]

    if ignore_id:
        sql_conflict += " AND id != %s"
        params.append(ignore_id)

    cursor.execute(sql_conflict, tuple(params))
    conflict = cursor.fetchone()

    cursor.close()
    conn.close()

    if conflict:
        return "ALREADY_BOOKED"

    return "OK"

def ajouter_rdv(data):
    state = rdv_is_valid(data)

    if state == "INACTIVE":
        return {"error": "INACTIVE"}

    if state == "NOT_AVAILABLE":
        return {"error": "NOT_AVAILABLE"}

    if state == "ALREADY_BOOKED":
        return {"error": "ALREADY_BOOKED"}

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO rendezvous
        (patient_id, medecin_id, date_rdv, heure_rdv, statut, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data.get("patient_id"),
        data.get("medecin_id"),
        data.get("date_rdv"),
        data.get("heure_rdv"),
        data.get("statut") or "en_attente",
        data.get("notes"),
    ))

    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True}


def editer_rdv(rdv_id, data):
    state = rdv_is_valid(data, ignore_id=rdv_id)

    if state == "INACTIVE":
        return {"error": "INACTIVE"}

    if state == "NOT_AVAILABLE":
        return {"error": "NOT_AVAILABLE"}

    if state == "ALREADY_BOOKED":
        return {"error": "ALREADY_BOOKED"}


    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE rendezvous
        SET patient_id=%s,
            medecin_id=%s,
            date_rdv=%s,
            heure_rdv=%s,
            statut=%s,
            notes=%s
        WHERE id=%s
    """, (
        data.get("patient_id"),
        data.get("medecin_id"),
        data.get("date_rdv"),
        data.get("heure_rdv"),
        data.get("statut"),
        data.get("notes"),
        rdv_id
    ))

    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True}


def supprimer_rdv(rdv_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rendezvous WHERE id = %s", (rdv_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return True


# =====================================================
# ✅ DISPONIBILITES
# =====================================================

def get_disponibilites(medecin_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT date_disponible, heure_debut, heure_fin
        FROM disponibilites_medecin
        WHERE medecin_id = %s
    """, (medecin_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "date": str(r["date_disponible"]),
            "heure_debut": str(r["heure_debut"]),
            "heure_fin": str(r["heure_fin"])
        }
        for r in rows
    ]


# =====================================================
# ✅ SERVICES
# =====================================================

def liste_services():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM services")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # ✅ Convert Decimal → float
    for row in rows:
        if isinstance(row.get("prix_unitaire"), Decimal):
            row["prix_unitaire"] = float(row["prix_unitaire"])

    return rows

# =====================================================
# ✅ NORMALISATION FACTURES
# =====================================================

def normalize_facture(row):
    if row is None:
        return None

    data = dict(row)

    # Convert Decimal → float
    if isinstance(data.get("montant_total"), Decimal):
        data["montant_total"] = float(data["montant_total"])

    # Convertir date → string
    if data.get("date_facture"):
        data["date_facture"] = data["date_facture"].isoformat()

    return data


# =====================================================
# ✅ NORMALISATION FACTURES
# =====================================================

def normalize_facture(row):
    if row is None:
        return None

    data = dict(row)

    # Convert Decimal → float
    if isinstance(data.get("montant_total"), Decimal):
        data["montant_total"] = float(data["montant_total"])

    # Convertir date → string
    if data.get("date_facture"):
        data["date_facture"] = data["date_facture"].isoformat()

    return data


# =====================================================
# ✅ FONCTIONS FACTURES
# =====================================================

def liste_factures(search=""):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        cursor.execute("""
            SELECT f.id,
                   f.services,
                   f.montant_total,
                   f.statut,
                   f.moyen_paiement,
                   f.date_facture,
                   p.nom AS patient_nom
            FROM factures f
            JOIN rendezvous r ON f.rdv_id = r.id
            JOIN patients p ON r.patient_id = p.id
            WHERE p.nom LIKE %s
               OR f.statut LIKE %s
               OR f.moyen_paiement LIKE %s
               OR f.id LIKE %s
            ORDER BY f.date_facture DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))
    else:
        cursor.execute("""
            SELECT f.id,
                   f.services,
                   f.montant_total,
                   f.statut,
                   f.moyen_paiement,
                   f.date_facture,
                   p.nom AS patient_nom
            FROM factures f
            JOIN rendezvous r ON f.rdv_id = r.id
            JOIN patients p ON r.patient_id = p.id
            ORDER BY f.date_facture DESC
        """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [normalize_facture(row) for row in rows]



def get_facture(facture_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            f.*,
            p.nom AS patient_nom,
            p.email AS patient_email,
            p.telephone AS patient_telephone,
            m.nom AS medecin_nom,
            m.specialite AS medecin_specialite,
            m.email AS medecin_email,
            m.telephone AS medecin_telephone,
            m.tarif_consultation  -- ✅ NOUVEAU : tarif du médecin
        FROM factures f
        JOIN rendezvous r ON f.rdv_id = r.id
        JOIN patients p ON r.patient_id = p.id
        JOIN medecins m ON r.medecin_id = m.id
        WHERE f.id = %s
    """, (facture_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        for key, value in row.items():

            # Convertir dates → string
            if hasattr(value, "isoformat"):
                row[key] = value.isoformat()
            
            # Convertir Decimal → float
            elif isinstance(value, Decimal):
                row[key] = float(value)

        # Forcer la conversion du tarif consultation si nécessaire
        if "tarif_consultation" in row:
            try:
                row["tarif_consultation"] = float(row["tarif_consultation"])
            except:
                pass

    return row



def ajouter_facture(data):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO factures 
        (rdv_id, statut, moyen_paiement, services, montant_total, date_facture)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data.get("rdv_id"),
        data.get("statut"),
        data.get("moyen_paiement"),
        data.get("services"),
        data.get("montant_total"),
        data.get("date_facture")
    ))

    conn.commit()
    facture_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return {"success": True, "facture_id": facture_id}


def editer_facture(facture_id, data):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE factures
        SET statut=%s,
            moyen_paiement=%s,
            services=%s,
            montant_total=%s
        WHERE id=%s
    """, (
        data.get("statut"),
        data.get("moyen_paiement"),
        data.get("services"),
        data.get("montant_total"),
        facture_id
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True}


def supprimer_facture(facture_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM factures WHERE id = %s", (facture_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return True

def get_services_facture(facture_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT services
        FROM factures
        WHERE id = %s
    """, (facture_id,))

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row or not row["services"]:
        return []

    services_raw = row["services"].split(',')
    services_list = []

    for item in services_raw:
        item = item.strip()
        if ':' not in item or item == "":
            continue  # ✅ ignore les entrées invalides

        name, qty = item.split(':')
        services_list.append({
            "nom": name.strip(),
            "quantite": int(qty.strip())
        })

    return services_list
# =====================================================
# ✅ NORMALISATION ADMIN
# =====================================================

def normalize_admin(row):
    if row is None:
        return None
    
    data = dict(row)

    # Convertir les dates en string
    if data.get("date_creation") and hasattr(data["date_creation"], "isoformat"):
        data["date_creation"] = data["date_creation"].isoformat()

    if data.get("last_login") and hasattr(data["last_login"], "isoformat"):
        data["last_login"] = data["last_login"].isoformat()

    return data


# ... tout le code précédent (medecins / patients / rdv / factures) inchangé ...


# =====================================================
# ✅ NORMALISATION ADMIN
# =====================================================

def normalize_admin(row):
    if row is None:
        return None
    
    data = dict(row)

    # Convertir les dates en string
    if data.get("date_creation") and hasattr(data["date_creation"], "isoformat"):
        data["date_creation"] = data["date_creation"].isoformat()

    if data.get("last_login") and hasattr(data["last_login"], "isoformat"):
        data["last_login"] = data["last_login"].isoformat()

    # photo est déjà une chaîne → rien à faire
    return data


# =====================================================
# ✅ FONCTIONS ADMIN
# =====================================================

def get_admin():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nom_complet, email, telephone, username, date_creation, last_login, photo
        FROM admin
        LIMIT 1
    """)
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return normalize_admin(row)


def update_admin(data):
    conn = create_connection()
    cursor = conn.cursor()

    # Si une nouvelle photo est fournie → on met à jour aussi `photo`
    if data.get("photo"):
        cursor.execute("""
            UPDATE admin
            SET nom_complet = %s,
                email = %s,
                telephone = %s,
                username = %s,
                photo = %s
            WHERE id = 1
        """, (
            data.get("nom_complet"),
            data.get("email"),
            data.get("telephone"),
            data.get("username"),
            data.get("photo")
        ))
    else:
        # Pas de nouvelle photo → on garde l'ancienne
        cursor.execute("""
            UPDATE admin
            SET nom_complet = %s,
                email = %s,
                telephone = %s,
                username = %s
            WHERE id = 1
        """, (
            data.get("nom_complet"),
            data.get("email"),
            data.get("telephone"),
            data.get("username")
        ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True}


def update_admin_password(current_pwd, new_pwd):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT password FROM admin WHERE id = 1")
    admin = cursor.fetchone()

    if not admin:
        cursor.close()
        conn.close()
        return {"error": "ADMIN_NOT_FOUND"}

    hashed = admin["password"].encode("utf-8")

    # ✅ Vérifier mot de passe actuel
    if not bcrypt.checkpw(current_pwd.encode("utf-8"), hashed):
        cursor.close()
        conn.close()
        return {"error": "WRONG_PASSWORD"}

    # ✅ Générer hash du nouveau mot de passe
    new_hashed = bcrypt.hashpw(new_pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # ✅ Mise à jour en BDD
    cursor.execute("UPDATE admin SET password = %s WHERE id = 1", (new_hashed,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"success": True}


def update_last_login():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE admin SET last_login = NOW() WHERE id = 1")
    conn.commit()

    cursor.close()
    conn.close()

    return True
# =====================================================
# ✅ Statistiques
# =====================================================

def get_stats():
    conn = create_connection()
    cursor = conn.cursor()

    # ✅ Médecins
    cursor.execute("SELECT COUNT(*) FROM medecins")
    total_medecins = cursor.fetchone()[0]

    # ✅ Patients
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

    # ✅ Rendez-vous aujourd'hui
    cursor.execute("SELECT COUNT(*) FROM rendezvous WHERE date_rdv = CURDATE()")
    rdv_aujourd_hui = cursor.fetchone()[0]

    # ✅ Factures totales
    cursor.execute("SELECT COUNT(*) FROM factures")
    factures_totales = cursor.fetchone()[0]

    # ✅ Factures payées
    cursor.execute("SELECT COUNT(*) FROM factures WHERE statut = 'payé'")
    factures_payees = cursor.fetchone()[0]

    # ✅ Factures en attente
    cursor.execute("SELECT COUNT(*) FROM factures WHERE statut IN ('non_payé', 'en_attente')")
    factures_en_attente = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {
        "total_medecins": total_medecins,
        "total_patients": total_patients,
        "rdv_aujourd_hui": rdv_aujourd_hui,
        "factures_totales": factures_totales,
        "factures_payees": factures_payees,
        "factures_en_attente": factures_en_attente
    }
# =====================================================
# ✅ NORMALISATION TACHES
# =====================================================

def normalize_tache(row):
    if row is None:
        return None

    data = dict(row)

    # Convertir la date si nécessaire
    if data.get("date_creation") and hasattr(data["date_creation"], "isoformat"):
        data["date_creation"] = data["date_creation"].isoformat()

    return data


# =====================================================
# ✅ FONCTIONS TACHES
# =====================================================

def liste_taches():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM taches ORDER BY date_creation DESC")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [normalize_tache(row) for row in rows]


def get_tache(tache_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM taches WHERE id = %s", (tache_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return normalize_tache(row)


def ajouter_tache(data):
    """
    Ajoute une tâche avec titre et statut.
    Statut attendu : 'à faire', 'en cours', ou 'terminée'
    """
    conn = create_connection()
    cursor = conn.cursor()

    titre = data.get("titre")
    statut = data.get("statut", "à faire")  # ✅ Valeur par défaut

    if not titre:
        return {"success": False, "error": "TITRE_OBLIGATOIRE"}

    try:
        cursor.execute("""
            INSERT INTO taches (titre, statut)
            VALUES (%s, %s)
        """, (titre, statut))

        conn.commit()
        tache_id = cursor.lastrowid
        
        cursor.close()
        conn.close()

        return {"success": True, "tache_id": tache_id}
    
    except Exception as e:
        cursor.close()
        conn.close()
        print(f"❌ Erreur ajouter_tache: {e}")
        return {"success": False, "error": str(e)}


def editer_tache(tache_id, data):
    """
    Modifie une tâche existante.
    Statut attendu : 'à faire', 'en cours', ou 'terminée'
    """
    conn = create_connection()
    cursor = conn.cursor()

    titre = data.get("titre")
    statut = data.get("statut")

    if not titre:
        cursor.close()
        conn.close()
        return {"success": False, "error": "TITRE_OBLIGATOIRE"}

    try:
        cursor.execute("""
            UPDATE taches
            SET titre=%s, statut=%s
            WHERE id=%s
        """, (titre, statut, tache_id))

        conn.commit()
        cursor.close()
        conn.close()

        return {"success": True}
    
    except Exception as e:
        cursor.close()
        conn.close()
        print(f"❌ Erreur editer_tache: {e}")
        return {"success": False, "error": str(e)}


def supprimer_tache(tache_id):
    """
    Supprime une tâche par son ID.
    """
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM taches WHERE id=%s", (tache_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return {"success": True}
    
    except Exception as e:
        cursor.close()
        conn.close()
        print(f"❌ Erreur supprimer_tache: {e}")
        return {"success": False, "error": str(e)}

def liste_rdv_aujourdhui():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT r.*, 
               p.nom AS patient_nom,
               m.nom AS medecin_nom
        FROM rendezvous r
        JOIN patients p ON r.patient_id = p.id
        JOIN medecins m ON r.medecin_id = m.id
        WHERE r.date_rdv = CURDATE()
        ORDER BY r.heure_rdv ASC
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    # ✅ Normalisation pour XML-RPC
    normalized = []
    for r in rows:
        # ✅ Convertir date
        if isinstance(r.get("date_rdv"), (datetime.date, datetime.datetime)):
            r["date_rdv"] = r["date_rdv"].strftime("%Y-%m-%d")

        # ✅ Convertir heure_rdv (timedelta → "HH:MM")
        heure = r.get("heure_rdv")
        if isinstance(heure, timedelta):
            total_seconds = int(heure.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            r["heure_rdv"] = f"{hours:02d}:{minutes:02d}"
        elif hasattr(heure, "strftime"):
            r["heure_rdv"] = heure.strftime("%H:%M")
        else:
            r["heure_rdv"] = str(heure)

        normalized.append(r)

    cursor.close()
    conn.close()
    return normalized





# =====================================================
# ✅ LANCEMENT SERVEUR RPC
# =====================================================

if __name__ == "__main__":
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    print("Serveur RPC lance sur http://localhost:8000")

    # Médecins
    server.register_function(liste_medecins, "liste_medecins")
    server.register_function(get_medecin, "get_medecin")
    server.register_function(ajouter_medecin, "ajouter_medecin")
    server.register_function(editer_medecin, "editer_medecin")
    server.register_function(supprimer_medecin, "supprimer_medecin")

    # Patients
    server.register_function(liste_patients, "liste_patients")
    server.register_function(get_patient, "get_patient")
    server.register_function(ajouter_patient, "ajouter_patient")
    server.register_function(editer_patient, "editer_patient")
    server.register_function(supprimer_patient, "supprimer_patient")

    # RDV
    server.register_function(liste_rdv, "liste_rdv")
    server.register_function(get_rdv, "get_rdv")
    server.register_function(ajouter_rdv, "ajouter_rdv")
    server.register_function(editer_rdv, "editer_rdv")
    server.register_function(supprimer_rdv, "supprimer_rdv")

    # Disponibilités
    server.register_function(get_disponibilites, "get_disponibilites")
    # Listes services
    server.register_function(liste_services, "liste_services")

    # Factures
    server.register_function(liste_factures, "liste_factures")
    server.register_function(get_facture, "get_facture")
    server.register_function(ajouter_facture, "ajouter_facture")
    server.register_function(editer_facture, "editer_facture")
    server.register_function(supprimer_facture, "supprimer_facture")
    server.register_function(get_services_facture, "get_services_facture")
    # Admin
    server.register_function(get_admin, "get_admin")
    server.register_function(update_admin, "update_admin")
    server.register_function(update_admin_password, "update_admin_password")
    server.register_function(update_last_login, "update_last_login")
    # Statistiques
    server.register_function(get_stats, "get_stats")
    # Tâches
    server.register_function(liste_taches, "liste_taches")
    server.register_function(get_tache, "get_tache")
    server.register_function(ajouter_tache, "ajouter_tache")
    server.register_function(editer_tache, "editer_tache")
    server.register_function(supprimer_tache, "supprimer_tache")
    # Rdv_du_jour
    server.register_function(liste_rdv_aujourdhui, "liste_rdv_aujourdhui")

    server.register_function(liste_specialisations, "liste_specialisations")
    server.serve_forever()
