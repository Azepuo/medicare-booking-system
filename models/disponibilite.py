
from database.connection import get_cursor


class Disponibilite:

    @staticmethod
    def get_all(medecin_id):
        with get_cursor() as (conn, cur):
            cur.execute("""
                SELECT id, jour_semaine, heure_debut, heure_fin,
                       TIMEDIFF(heure_fin, heure_debut) AS duree
                FROM disponibilites
                WHERE medecin_id = %s
                ORDER BY FIELD(jour_semaine,
                    'lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche'),
                    heure_debut
            """, (medecin_id,))
            return cur.fetchall()

    @staticmethod
    def get_one(dispo_id):
        with get_cursor() as (conn, cur):
            cur.execute("""
                SELECT id, jour_semaine, heure_debut, heure_fin
                FROM disponibilites
                WHERE id = %s
            """, (dispo_id,))
            return cur.fetchone()

    @staticmethod
    def create(data, medecin_id):
        with get_cursor() as (conn, cur):
            cur.execute("""
                INSERT INTO disponibilites (medecin_id, jour_semaine, heure_debut, heure_fin)
                VALUES (%s, %s, %s, %s)
            """, (
                medecin_id,
                data["jour_semaine"],
                data["heure_debut"],
                data["heure_fin"]
            ))
            return cur.lastrowid

    @staticmethod
    def update(dispo_id, data):
        with get_cursor() as (conn, cur):
            cur.execute("""
                UPDATE disponibilites
                SET jour_semaine = %s, heure_debut = %s, heure_fin = %s
                WHERE id = %s
            """, (
                data["jour_semaine"],
                data["heure_debut"],
                data["heure_fin"],
                dispo_id
            ))
            return cur.rowcount > 0

    @staticmethod
    def delete(dispo_id):
        with get_cursor() as (conn, cur):
            cur.execute("DELETE FROM disponibilites WHERE id = %s", (dispo_id,))
            return cur.rowcount > 0

    @staticmethod
    def get_stats(medecin_id):
        with get_cursor() as (conn, cur):
            cur.execute("""
                SELECT 
                    SUM(TIME_TO_SEC(TIMEDIFF(heure_fin, heure_debut))) / 3600 AS heures_semaine,
                    COUNT(DISTINCT jour_semaine) AS jours_travailles,
                    COUNT(*) AS total_creneaux
                FROM disponibilites
                WHERE medecin_id = %s
            """, (medecin_id,))
            return cur.fetchone()
