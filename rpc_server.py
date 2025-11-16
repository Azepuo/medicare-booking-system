# rpc_server.py ---Admin---

from xmlrpc.server import SimpleXMLRPCServer
from database.connection import create_connection
from decimal import Decimal

def normalize_medecin(row):
    """Convertit les types MySQL en types simples (str, int, float) pour RPC."""
    if row is None:
        return None
    data = dict(row)

    # date_inscription en string "YYYY-MM-DD"
    if "date_inscription" in data and data["date_inscription"] is not None:
        data["date_inscription"] = data["date_inscription"].isoformat()

    # tarif_consultation en float si Decimal
    if "tarif_consultation" in data and isinstance(data["tarif_consultation"], Decimal):
        data["tarif_consultation"] = float(data["tarif_consultation"])

    return data


# --------- FONCTIONS MEDECINS POUR RPC --------- #

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
    """
    data = {
        "nom": "...",
        "email": "...",
        "telephone": "...",
        "specialite": "...",
        "annees_experience": "...",
        "tarif_consultation": "...",
        "description": "...",
        "statut": "...",
        "date_inscription": "YYYY-MM-DD" ou None
    }
    """
    conn = create_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO medecins
        (nom, email, telephone, specialite,
         annees_experience, tarif_consultation,
         description, statut, date_inscription)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        data.get("date_inscription"),
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
            description=%s, statut=%s, date_inscription=%s
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
        data.get("date_inscription"),
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


# --------- LANCEMENT DU SERVEUR RPC --------- #

if __name__ == "__main__":
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    print("🚀 Serveur RPC lancé sur http://localhost:8000")

    # Enregistrer les fonctions RPC
    server.register_function(liste_medecins, "liste_medecins")
    server.register_function(get_medecin, "get_medecin")
    server.register_function(ajouter_medecin, "ajouter_medecin")
    server.register_function(editer_medecin, "editer_medecin")
    server.register_function(supprimer_medecin, "supprimer_medecin")

    server.serve_forever()
