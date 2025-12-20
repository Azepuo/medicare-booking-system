# app/rpc_medecin/disponibilites_rpc_methods.py
from database.connection_m import create_connection
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from datetime import timedelta, datetime

# ----------------- CONTEXT MANAGER -----------------
@contextmanager
def get_cursor():
    conn = create_connection()
    if not conn:
        raise RuntimeError("Impossible de se connecter à la base")
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

# ----------------- HELPERS -----------------
def _convert_timedelta_to_str(td):
    """Convertit un timedelta en string HH:MM:SS"""
    if isinstance(td, timedelta):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return str(td)

def _row_to_dispo(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not row:
        return None
    
    # Récupérer les valeurs
    heure_debut = row.get('heure_debut')
    heure_fin = row.get('heure_fin')
    
    # Convertir les timedelta en strings
    heure_debut_str = _convert_timedelta_to_str(heure_debut)
    heure_fin_str = _convert_timedelta_to_str(heure_fin)
    
    return {
        'id': row.get('id'),
        'user_id': row.get('user_id'),  # CHANGÉ: medecin_id -> user_id
        'jour_semaine': row.get('jour_semaine'),
        'heure_debut': heure_debut_str,
        'heure_fin': heure_fin_str,
        'heure_debut_display': heure_debut_str[:5] if heure_debut_str else '',  # Format HH:MM
        'heure_fin_display': heure_fin_str[:5] if heure_fin_str else '',  # Format HH:MM
        'date_creation': row.get('date_creation')
    }

# ----------------- LIST -----------------
def list_dispo(user_id: int, today_only: bool = False) -> List[Dict[str, Any]]:
    """Liste les disponibilités pour un utilisateur"""
    with get_cursor() as (conn, cur):
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
        
        jour_aujourdhui = None
        if today_only:
            from datetime import datetime
            jour_aujourdhui = jours_fr.get(datetime.now().strftime('%A'))
        
        if today_only and jour_aujourdhui:
            # Disponibilités pour aujourd'hui seulement
            cur.execute("""
                SELECT * FROM disponibilites 
                WHERE user_id = %s AND jour_semaine = %s
                ORDER BY heure_debut
            """, (user_id, jour_aujourdhui))
        else:
            # Toutes les disponibilités
            cur.execute("""
                SELECT * FROM disponibilites 
                WHERE user_id = %s
                ORDER BY 
                    FIELD(jour_semaine, 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'),
                    heure_debut
            """, (user_id,))
        
        rows = cur.fetchall()
        result = []
        for row in rows:
            dispo = _row_to_dispo(row)
            if dispo:
                result.append(dispo)
        
        return result
# ----------------- GET SINGLE -----------------
def get_dispo(dispo_id: int) -> Optional[Dict[str, Any]]:
    with get_cursor() as (conn, cur):
        cur.execute("SELECT * FROM disponibilites WHERE id = %s", (dispo_id,))
        row = cur.fetchone()
        return _row_to_dispo(row)

# ----------------- CREATE -----------------
def create_dispo(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = payload.get('user_id')  # CHANGÉ: medecin_id -> user_id
    jour_semaine = payload.get('jour_semaine')
    heure_debut = payload.get('heure_debut')
    heure_fin = payload.get('heure_fin')
    
    if not user_id or not jour_semaine or not heure_debut or not heure_fin:
        raise ValueError("user_id, jour_semaine, heure_debut et heure_fin sont requis")
    
    # Vérifier les conflits
    with get_cursor() as (conn, cur):
        cur.execute("""
            SELECT * FROM disponibilites 
            WHERE user_id = %s AND jour_semaine = %s 
            AND (
                (heure_debut <= %s AND heure_fin > %s) OR
                (heure_debut < %s AND heure_fin >= %s) OR
                (heure_debut >= %s AND heure_fin <= %s)
            )
        """, (
            user_id, jour_semaine,
            heure_debut, heure_debut,
            heure_fin, heure_fin,
            heure_debut, heure_fin
        ))
        
        existing = cur.fetchone()
        if existing:
            raise ValueError("Une disponibilité existe déjà pour cette plage horaire")
    
    # Insérer
    sql = """
        INSERT INTO disponibilites (user_id, jour_semaine, heure_debut, heure_fin)
        VALUES (%s, %s, %s, %s)
    """
    with get_cursor() as (conn, cur):
        cur.execute(sql, (user_id, jour_semaine, heure_debut, heure_fin))
        new_id = cur.lastrowid
        cur.execute("SELECT * FROM disponibilites WHERE id = %s", (new_id,))
        row = cur.fetchone()
        return _row_to_dispo(row)

# ----------------- UPDATE -----------------
def update_dispo(dispo_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    allowed = ["jour_semaine", "heure_debut", "heure_fin"]
    sets = []
    params = []
    
    for field in allowed:
        if field in data:
            sets.append(f"{field} = %s")
            params.append(data[field])
    
    if not sets:
        return get_dispo(dispo_id)
    
    params.append(dispo_id)
    sql = "UPDATE disponibilites SET " + ", ".join(sets) + " WHERE id = %s"
    
    with get_cursor() as (conn, cur):
        cur.execute(sql, tuple(params))
        cur.execute("SELECT * FROM disponibilites WHERE id = %s", (dispo_id,))
        row = cur.fetchone()
        return _row_to_dispo(row)

# ----------------- DELETE -----------------
def delete_dispo(dispo_id: int) -> bool:
    with get_cursor() as (conn, cur):
        cur.execute("SELECT 1 FROM disponibilites WHERE id = %s", (dispo_id,))
        if not cur.fetchone():
            return False
        cur.execute("DELETE FROM disponibilites WHERE id = %s", (dispo_id,))
        return True