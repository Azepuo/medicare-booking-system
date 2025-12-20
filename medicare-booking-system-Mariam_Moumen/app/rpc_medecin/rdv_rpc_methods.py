# app/rpc_medecin/rdv_rpc_methods.py
from database.connection import create_connection
from datetime import datetime, date
from contextlib import contextmanager

@contextmanager
def get_cursor():
    conn = create_connection()
    if not conn:
        raise RuntimeError("Impossible de se connecter à la base de données")
    try:
        cur = conn.cursor(dictionary=True)
        yield conn, cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        try:
            cur.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass

def _row_to_rdv(row):
    """Convertir une ligne de rendez-vous en dictionnaire"""
    if not row:
        return None
    result = {
        'id': row.get('id'),
        'patient_id': row.get('patient_id'),
        'user_id': row.get('user_id'),  # ✅ user_id au lieu de medecin_id
        'date_heure': row.get('date_heure'),
        'statut': row.get('statut', 'En attente'),
        'notes': row.get('notes', ''),
        'patient_nom': row.get('patient_nom', ''),
        'patient_telephone': row.get('patient_telephone', '')
    }
    
    # Formatter la date si nécessaire
    if result['date_heure'] and isinstance(result['date_heure'], (datetime, date)):
        result['date_heure'] = result['date_heure'].strftime('%Y-%m-%dT%H:%M')
        result['date_heure_display'] = result['date_heure'].strftime('%Y-%m-%d %H:%M')
    
    return result

# ----------------- LIST -----------------
def list_rdv(user_id, today=False):
    """Lister les rendez-vous d'un médecin (par user_id)"""
    with get_cursor() as (conn, cur):
        if today:
            today_date = date.today()
            query = """
                SELECT r.*, p.nom as patient_nom, p.telephone as patient_telephone
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                WHERE r.user_id = %s AND DATE(r.date_heure) = %s
                ORDER BY r.date_heure
            """
            cur.execute(query, (user_id, today_date))
        else:
            query = """
                SELECT r.*, p.nom as patient_nom, p.telephone as patient_telephone
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                WHERE r.user_id = %s
                ORDER BY r.date_heure
            """
            cur.execute(query, (user_id,))
        
        rows = cur.fetchall()
        return [_row_to_rdv(r) for r in rows if r]

# ----------------- GET SINGLE -----------------
def get_rdv(rdv_id, user_id):
    """Récupérer un rendez-vous spécifique"""
    with get_cursor() as (conn, cur):
        query = """
            SELECT r.*, p.nom as patient_nom, p.telephone as patient_telephone
            FROM rendezvous r
            JOIN patients p ON r.patient_id = p.id
            WHERE r.id = %s AND r.user_id = %s
        """
        cur.execute(query, (rdv_id, user_id))
        row = cur.fetchone()
        return _row_to_rdv(row)

# ----------------- CREATE -----------------
def create_rdv(payload):
    """Créer un nouveau rendez-vous"""
    with get_cursor() as (conn, cur):
        query = """
            INSERT INTO rendezvous (patient_id, user_id, date_heure, statut, notes)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (
            payload['patient_id'],
            payload['user_id'],  # ✅ user_id directement
            payload['date_heure'],
            payload['statut'],
            payload['notes']
        ))
        
        # Récupérer le rendez-vous créé
        rdv_id = cur.lastrowid
        return get_rdv(rdv_id, payload['user_id'])

# ----------------- UPDATE -----------------
def update_rdv(rdv_id, user_id, payload):
    """Mettre à jour un rendez-vous"""
    with get_cursor() as (conn, cur):
        # Vérifier que le rendez-vous existe et appartient à l'utilisateur
        cur.execute("SELECT id FROM rendezvous WHERE id = %s AND user_id = %s", (rdv_id, user_id))
        if not cur.fetchone():
            return None
        
        # Construire la requête de mise à jour
        allowed_fields = ['patient_id', 'date_heure', 'statut', 'notes']
        updates = []
        params = []
        
        for field in allowed_fields:
            if field in payload:
                updates.append(f"{field} = %s")
                params.append(payload[field])
        
        if not updates:
            return get_rdv(rdv_id, user_id)
        
        params.append(rdv_id)
        query = f"UPDATE rendezvous SET {', '.join(updates)} WHERE id = %s"
        
        cur.execute(query, tuple(params))
        return get_rdv(rdv_id, user_id)

# ----------------- DELETE -----------------
def delete_rdv(rdv_id, user_id):
    """Supprimer un rendez-vous"""
    with get_cursor() as (conn, cur):
        # Vérifier que le rendez-vous existe et appartient à l'utilisateur
        cur.execute("SELECT id FROM rendezvous WHERE id = %s AND user_id = %s", (rdv_id, user_id))
        if not cur.fetchone():
            return False
        
        cur.execute("DELETE FROM rendezvous WHERE id = %s", (rdv_id,))
        return True