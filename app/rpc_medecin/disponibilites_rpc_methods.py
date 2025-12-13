# app/rpc_medecin/disponibilites_rpc_methods.py

from database.connection_m import get_cursor

# ========================================================
# LISTE DE TOUTES LES DISPONIBILITÉS
# ========================================================
def list_disponibilites():
    with get_cursor() as (conn, cur):
        cur.execute("SELECT * FROM disponibilites ORDER BY id DESC")
        return cur.fetchall()

# ========================================================
# OBTENIR UNE DISPONIBILITÉ
# ========================================================
def get_disponibilite(dispo_id):
    with get_cursor() as (conn, cur):
        cur.execute("SELECT * FROM disponibilites WHERE id = %s", (dispo_id,))
        return cur.fetchone()

# ========================================================
# CRÉER UNE DISPONIBILITÉ
# ========================================================
def create_disponibilite(data):
    with get_cursor() as (conn, cur):
        cur.execute("""
            INSERT INTO disponibilites (jour, heure_debut, heure_fin, medecin_id)
            VALUES (%s, %s, %s, %s)
        """, (
            data.get("jour"),
            data.get("heure_debut"),
            data.get("heure_fin"),
            data.get("medecin_id")
        ))
        dispo_id = cur.lastrowid
        conn.commit()

        return get_disponibilite(dispo_id)

# ========================================================
# METTRE À JOUR UNE DISPONIBILITÉ
# ========================================================
def update_disponibilite(dispo_id, data):
    with get_cursor() as (conn, cur):
        cur.execute("""
            UPDATE disponibilites
            SET jour = %s, heure_debut = %s, heure_fin = %s
            WHERE id = %s
        """, (
            data.get("jour"),
            data.get("heure_debut"),
            data.get("heure_fin"),
            dispo_id
        ))
        conn.commit()

        return get_disponibilite(dispo_id)

# ========================================================
# SUPPRIMER UNE DISPONIBILITÉ
# ========================================================
def delete_disponibilite(dispo_id):
    with get_cursor() as (conn, cur):
        cur.execute("DELETE FROM disponibilites WHERE id = %s", (dispo_id,))
        conn.commit()
        return cur.rowcount > 0
