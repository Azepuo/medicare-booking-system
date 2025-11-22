# rpc_server.py ---Admin---

from xmlrpc.server import SimpleXMLRPCServer
from database.connection import create_connection
from decimal import Decimal


# =====================================================
# ✅ NORMALISATION MEDECINS
# =====================================================

def normalize_medecin(row):
    if row is None:
        return None

    data = dict(row)

    for key, value in data.items():
        # Convertir les Decimal en float
        if isinstance(value, Decimal):
            data[key] = float(value)

    # Convertir date_inscription en string
    if "date_inscription" in data and data["date_inscription"] is not None:
        data["date_inscription"] = data["date_inscription"].isoformat()

    return data

# =====================================================
# ✅ FONCTIONS MEDECINS POUR RPC
# =====================================================

def liste_medecins():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM medecins")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [normalize_medecin(row) for row in rows]


def get_medecin(medecin_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM medecins WHERE id = %s", (medecin_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return normalize_medecin(row)


def ajouter_medecin(data):
    conn = create_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO medecins
        (nom, email, telephone, specialite,
         annees_experience, tarif_consultation,
         description, statut)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        data.get("nom"),
        data.get("email"),
        data.get("telephone"),
        data.get("specialite"),
        data.get("annees_experience"),
        data.get("tarif_consultation"),
        data.get("description"),
        data.get("statut"),
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def editer_medecin(medecin_id, data):
    conn = create_connection()
    cursor = conn.cursor()

    sql = """
        UPDATE medecins
        SET nom=%s, email=%s, telephone=%s, specialite=%s,
            annees_experience=%s, tarif_consultation=%s,
            description=%s, statut=%s
        WHERE id=%s
    """
    cursor.execute(sql, (
        data.get("nom"),
        data.get("email"),
        data.get("telephone"),
        data.get("specialite"),
        data.get("annees_experience"),
        data.get("tarif_consultation"),
        data.get("description"),
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
    cursor.execute("DELETE FROM medecins WHERE id = %s", (medecin_id,))
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

    if "date_naissance" in data and data["date_naissance"] is not None:
        data["date_naissance"] = data["date_naissance"].isoformat()

    if "date_inscription" in data and data["date_inscription"] is not None:
        data["date_inscription"] = data["date_inscription"].isoformat()

    return data



# =====================================================
# ✅ FONCTIONS PATIENTS POUR RPC
# =====================================================

def liste_patients():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [normalize_patient(row) for row in rows]


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

    sql = """
        INSERT INTO patients
        (nom, cin, email, telephone, sexe, date_naissance)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
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

    sql = """
        UPDATE patients
        SET nom=%s, cin=%s, email=%s, telephone=%s, sexe=%s,
            date_naissance=%s
        WHERE id=%s
    """
    cursor.execute(sql, (
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
# ✅ LANCEMENT DU SERVEUR RPC
# =====================================================

if __name__ == "__main__":
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    print("🚀 Serveur RPC lancé sur http://localhost:8000")

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

    server.serve_forever()
