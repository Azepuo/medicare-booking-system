from xmlrpc.server import SimpleXMLRPCServer
from database.connection import create_connection
from decimal import Decimal
from datetime import timedelta
import bcrypt
import datetime
from datetime import date

import secrets
import string

from models import User
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass



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
    plain_password = "00000"
    hashed_password = bcrypt.hashpw(
    plain_password.encode("utf-8"),
    bcrypt.gensalt()
    ).decode("utf-8")

    email = data["email"].strip().lower()
    # 1️⃣ USER (authentification)
    cursor.execute("""
        INSERT INTO users (nom, email, telephone, password, role)
        VALUES (%s, %s, %s, %s, 'MEDECIN')
    """, (
        data["nom_complet"],
        email,
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
        email,
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


# =========================
# NORMALISATION PATIENT
# =========================
def normalize_patient(row):
    if not row:
        return None
    data = dict(row)
    if data.get("date_inscription"):
        data["date_inscription"] = data["date_inscription"].isoformat()
    return data


# =========================
# LISTE PATIENTS
# =========================
def liste_patients(search=""):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT
            p.id,
            u.nom,
            u.email,
            u.telephone,
            u.created_at AS date_inscription,
            p.sexe
        FROM patients p
        JOIN users u ON p.user_id = u.id
        WHERE u.role = 'PATIENT'
    """

    params = ()

    if search:
        sql += """
            AND (
                u.nom LIKE %s OR
                u.email LIKE %s OR
                u.telephone LIKE %s
            )
        """
        params = (f"%{search}%", f"%{search}%", f"%{search}%")

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [normalize_patient(r) for r in rows]


# =========================
# GET PATIENT
# =========================
def get_patient(patient_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.id,
            u.nom,
            u.email,
            u.telephone,
            u.created_at AS date_inscription,
            p.sexe
        FROM patients p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = %s
    """, (patient_id,))

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return normalize_patient(row)


# =========================
# AJOUT PATIENT (COMME MEDECIN)
# =========================
def ajouter_patient(data):
    if not data.get("nom") or not data.get("email"):
        raise Exception("DONNEES_INCOMPLETES")

    email = data["email"].strip().lower()
    plain_password = "00000"

    # ✅ UTILISER LE MODÈLE USER
    user = User(
        nom=data["nom"],
        email=email,
        role="PATIENT",
        telephone=data.get("telephone")
    )
    user.set_password(plain_password)
    user.save()

    user_id = user.id

    # 2️⃣ PATIENT
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients (user_id, nom, email, telephone, sexe)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        user_id,
        data["nom"],
        email,
        data.get("telephone"),
        data.get("sexe")
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "generated_password": plain_password
    }

# =========================
# EDIT PATIENT
# =========================
def editer_patient(patient_id, data):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM patients WHERE id = %s", (patient_id,))
    user_id = cursor.fetchone()[0]

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

    cursor.execute("""
        UPDATE patients
        SET sexe=%s
        WHERE id=%s
    """, (
        data.get("sexe"),
        patient_id
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True}


# =========================
# DELETE PATIENT
# =========================
def supprimer_patient(patient_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM patients WHERE id = %s", (patient_id,))
    user_id = cursor.fetchone()[0]

    cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True}



# =====================================================
# ✅ NORMALISATION RDV
# =====================================================
def normalize_rdv(row):
    if not row:
        return None

    data = dict(row)

    # ✅ Convertir TOUS les Decimal → float
    for k, v in data.items():
        if isinstance(v, Decimal):
            data[k] = float(v)

    # ✅ Formater les dates
    if data.get("date_heure") and hasattr(data["date_heure"], "strftime"):
        dt = data["date_heure"]
        data["date_rdv"] = dt.strftime("%Y-%m-%d")
        data["heure_rdv"] = dt.strftime("%H:%M")
        data["date_heure"] = dt.strftime("%Y-%m-%d %H:%M:%S")

    return data
# def normalize_rdv(row):
#     if not row:
#         return None

#     data = dict(row)

#     if data.get("date_heure") and hasattr(data["date_heure"], "strftime"):
#         dt = data["date_heure"]
#         data["date_rdv"] = dt.strftime("%Y-%m-%d")
#         data["heure_rdv"] = dt.strftime("%H:%M")
#         data["date_heure"] = dt.strftime("%Y-%m-%d %H:%M:%S")

#     return data


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
            ORDER BY r.date_heure DESC
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
            ORDER BY r.date_heure DESC
        """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [normalize_rdv(r) for r in rows]

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

def normalize_jour(jour):
    """
    Normalise le jour en français (lundi → dimanche)
    Accepte FR / EN / majuscules / minuscules
    """
    if not jour:
        return None

    jour = jour.strip().lower()

    mapping = {
        # Anglais → Français
        "monday": "lundi",
        "tuesday": "mardi",
        "wednesday": "mercredi",
        "thursday": "jeudi",
        "friday": "vendredi",
        "saturday": "samedi",
        "sunday": "dimanche",

        # Français
        "lundi": "lundi",
        "mardi": "mardi",
        "mercredi": "mercredi",
        "jeudi": "jeudi",
        "vendredi": "vendredi",
        "samedi": "samedi",
        "dimanche": "dimanche",
    }

    return mapping.get(jour)

# ✅ Fonction interne de vérification
def rdv_is_valid(data, ignore_id=None):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Médecin actif
    cursor.execute("SELECT statut FROM medecins WHERE id=%s", (data["medecin_id"],))
    med = cursor.fetchone()
    if not med or med["statut"] != "Actif":
        cursor.close()
        conn.close()
        return "MEDECIN_INACTIF"

    # 2️⃣ Date / Heure
    try:
        dt = datetime.datetime.strptime(data["date_heure"], "%Y-%m-%d %H:%M:%S")
    except Exception:
        cursor.close()
        conn.close()
        return "FORMAT_DATE_INVALIDE"

    # 🔹 Jour normalisé (FR)
    jour_raw = dt.strftime("%A")          # Monday / Tuesday / ...
    jour = normalize_jour(jour_raw)       # lundi / mardi / ...

    if not jour:
        cursor.close()
        conn.close()
        return "JOUR_INVALIDE"

    heure = dt.time()

    # 3️⃣ Vérifier disponibilité médecin
    cursor.execute("""
        SELECT *
        FROM disponibilites
        WHERE medecin_id = %s
          AND LOWER(jour_semaine) = %s
          AND %s BETWEEN heure_debut AND heure_fin
    """, (
        data["medecin_id"],
        jour,
        heure
    ))

    dispo = cursor.fetchone()
    if not dispo:
        cursor.close()
        conn.close()
        return "MEDECIN_NON_DISPONIBLE"

    # 4️⃣ Vérifier conflit RDV (30 minutes)
    cursor.execute("""
        SELECT id
        FROM rendezvous
        WHERE medecin_id = %s
          AND ABS(TIMESTAMPDIFF(MINUTE, date_heure, %s)) < 30
    """, (
        data["medecin_id"],
        data["date_heure"]
    ))

    conflict = cursor.fetchone()
    cursor.close()
    conn.close()

    if conflict and (not ignore_id or conflict["id"] != ignore_id):
        return "CRENEAU_DEJA_PRIS"

    return "OK"


def ajouter_rdv(data):
    # ✅ Vérifier que date_heure existe
    if "date_heure" not in data:
        return {"error": "DATE_HEURE_MANQUANTE"}

    # ✅ Valider les données
    state = rdv_is_valid(data)
    if state != "OK":
        return {"error": state}

    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO rendezvous
            (patient_id, medecin_id, date_heure, statut, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["patient_id"],
            data["medecin_id"],
            data["date_heure"],
            data.get("statut", "en_attente"),
            data.get("notes")
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return {"success": True}
    
    except Exception as e:
        if conn:
            conn.close()
        print(f"❌ Erreur ajouter_rdv: {e}")
        return {"error": "ERREUR_BDD"}




def editer_rdv(rdv_id, data):
    # ✅ Vérifier que date_heure existe
    if "date_heure" not in data:
        return {"error": "DATE_HEURE_MANQUANTE"}

    # ✅ Valider les données
    state = rdv_is_valid(data, ignore_id=rdv_id)
    if state != "OK":
        return {"error": state}

    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE rendezvous
            SET patient_id=%s,
                medecin_id=%s,
                date_heure=%s,
                statut=%s,
                notes=%s
            WHERE id=%s
        """, (
            data["patient_id"],
            data["medecin_id"],
            data["date_heure"],
            data.get("statut", "en_attente"),
            data.get("notes"),
            rdv_id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return {"success": True}
    
    except Exception as e:
        if conn:
            conn.close()
        print(f"❌ Erreur editer_rdv: {e}")
        return {"error": "ERREUR_BDD"}



def supprimer_rdv(rdv_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rendezvous WHERE id=%s", (rdv_id,))
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
        SELECT jour_semaine, heure_debut, heure_fin
        FROM disponibilites
        WHERE medecin_id = %s
    """, (medecin_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return rows



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
            s.nom AS medecin_specialite,  -- ✅ CHANGÉ : depuis la table specialisations
            m.email AS medecin_email,
            m.telephone AS medecin_telephone,
            m.tarif_consultation
        FROM factures f
        JOIN rendezvous r ON f.rdv_id = r.id
        JOIN patients p ON r.patient_id = p.id
        JOIN medecins m ON r.medecin_id = m.id
        LEFT JOIN specialisations s ON m.id_specialisation = s.id  -- ✅ AJOUTÉ
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

    # ✅ Validation du montant_total
    montant_total = data.get("montant_total", "0")
    
    # Nettoyer et convertir
    if isinstance(montant_total, str):
        montant_total = montant_total.strip()
    
    # Si vide ou None, mettre 0
    if not montant_total or montant_total == "" or montant_total == "0":
        cursor.close()
        conn.close()
        return {"error": "MONTANT_DOIT_ETRE_SUPERIEUR_A_ZERO"}
    
    # Convertir en float
    try:
        montant_total = float(montant_total)
    except (ValueError, TypeError):
        cursor.close()
        conn.close()
        return {"error": "MONTANT_INVALIDE"}
    
    # Vérifier que le montant est positif
    if montant_total <= 0:
        cursor.close()
        conn.close()
        return {"error": "MONTANT_DOIT_ETRE_POSITIF"}

    # Vérifier que des services sont fournis
    services = data.get("services", "").strip()
    if not services:
        cursor.close()
        conn.close()
        return {"error": "SERVICES_REQUIS"}

    try:
        cursor.execute("""
            INSERT INTO factures 
            (rdv_id, statut, moyen_paiement, services, montant_total, date_facture)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data.get("rdv_id"),
            data.get("statut", "non_payé"),
            data.get("moyen_paiement", "non_defini"),
            services,
            montant_total,  # ✅ Maintenant c'est un float valide
            data.get("date_facture")
        ))

        conn.commit()
        facture_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return {"success": True, "facture_id": facture_id}
    
    except Exception as e:
        if conn:
            conn.close()
        print(f"❌ Erreur ajouter_facture: {e}")
        return {"error": f"ERREUR_BDD: {str(e)}"}


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

# def normalize_admin(row):
#     if row is None:
#         return None
    
#     data = dict(row)

#     # Convertir les dates en string
#     if data.get("date_creation") and hasattr(data["date_creation"], "isoformat"):
#         data["date_creation"] = data["date_creation"].isoformat()

#     if data.get("last_login") and hasattr(data["last_login"], "isoformat"):
#         data["last_login"] = data["last_login"].isoformat()

    # return data
# 

# ... tout le code précédent (medecins / patients / rdv / factures) inchangé ...


# =====================================================
# ✅ NORMALISATION ADMIN
# =====================================================

def normalize_admin(row):
    if not row:
        return None

    data = dict(row)

    if data.get("created_at"):
        data["created_at"] = data["created_at"].isoformat()

    if data.get("last_login"):
        data["last_login"] = data["last_login"].isoformat()

    return data



# =====================================================
# ✅ FONCTIONS ADMIN
# =====================================================

def get_admin():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.id,
            u.nom,
            u.email,
            u.telephone,
            a.username,
            a.photo,
            a.last_login,
            u.created_at
        FROM admin a
        JOIN users u ON a.user_id = u.id
        WHERE u.role = 'ADMIN'
        LIMIT 1
    """)

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return normalize_admin(row)



def update_admin(data):
    conn = create_connection()
    cursor = conn.cursor()

    # 1️⃣ update USERS
    cursor.execute("""
        UPDATE users
        SET nom=%s,
            email=%s,
            telephone=%s
        WHERE role='ADMIN'
        LIMIT 1
    """, (
        data.get("nom_complet"),
        data.get("email"),
        data.get("telephone")
    ))

    # 2️⃣ update ADMIN
    if data.get("photo"):
        cursor.execute("""
            UPDATE admin
            SET username=%s,
                photo=%s
            WHERE user_id = (
                SELECT id FROM users WHERE role='ADMIN' LIMIT 1
            )
        """, (
            data.get("username"),
            data.get("photo")
        ))
    else:
        cursor.execute("""
            UPDATE admin
            SET username=%s
            WHERE user_id = (
                SELECT id FROM users WHERE role='ADMIN' LIMIT 1
            )
        """, (
            data.get("username"),
        ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True}



def update_admin_password(current_pwd, new_pwd):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, password
        FROM users
        WHERE role='ADMIN'
        LIMIT 1
    """)
    admin = cursor.fetchone()

    if not admin:
        cursor.close()
        conn.close()
        return {"error": "ADMIN_NOT_FOUND"}

    if not bcrypt.checkpw(current_pwd.encode(), admin["password"].encode()):
        cursor.close()
        conn.close()
        return {"error": "WRONG_PASSWORD"}

    new_hash = bcrypt.hashpw(new_pwd.encode(), bcrypt.gensalt()).decode()

    cursor.execute("""
        UPDATE users
        SET password=%s
        WHERE id=%s
    """, (new_hash, admin["id"]))

    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True}



def update_last_login():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE admin
        SET last_login = NOW()
        WHERE user_id = (
            SELECT id FROM users WHERE role='ADMIN' LIMIT 1
        )
    """)

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
    cursor.execute("SELECT COUNT(*) FROM rendezvous WHERE DATE(date_heure) = CURDATE()") 
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

    cursor.execute("""
        SELECT r.*, 
               p.nom AS patient_nom,
               m.nom AS medecin_nom
        FROM rendezvous r
        JOIN patients p ON r.patient_id = p.id
        JOIN medecins m ON r.medecin_id = m.id
        WHERE DATE(r.date_heure) = CURDATE()
        ORDER BY r.date_heure ASC
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [normalize_rdv(r) for r in rows]





# =====================================================
# ✅ LANCEMENT SERVEUR RPC
# =====================================================

if __name__ == "__main__":
    server = ThreadedXMLRPCServer(
        ("localhost", 8002),
        allow_none=True
    )
    print("🚀 RPC THREADED lancé sur http://localhost:8002")

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
