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
    
    # Gestion du format de date
    date_heure = row.get('date_heure')
    date_heure_display = None
    
    if date_heure:
        if isinstance(date_heure, (datetime, date)):
            date_heure_display = date_heure.strftime('%Y-%m-%d %H:%M')
            # Format pour les inputs datetime-local
            date_heure = date_heure.strftime('%Y-%m-%dT%H:%M')
        elif isinstance(date_heure, str):
            try:
                # Si c'est déjà un string, essayer de le parser
                dt = datetime.fromisoformat(date_heure.replace('T', ' ').replace('Z', ''))
                date_heure_display = dt.strftime('%Y-%m-%d %H:%M')
                date_heure = dt.strftime('%Y-%m-%dT%H:%M')
            except:
                date_heure_display = date_heure
    
    result = {
        'id': row.get('id'),
        'patient_id': row.get('patient_id'),
        'medecin_id': row.get('medecin_id'),
        'date_heure': date_heure,
        'statut': row.get('statut', 'En attente'),
        'notes': row.get('notes', ''),
        'patient_nom': row.get('patient_nom', ''),
        'patient_prenom': row.get('patient_prenom', ''),
        'patient_telephone': row.get('patient_telephone', ''),
        'date_heure_display': date_heure_display or date_heure,
        'nom_complet': f"{row.get('patient_prenom', '')} {row.get('patient_nom', '')}".strip()
    }
    
    return result

# ----------------- LIST -----------------
def list_rdv(medecin_id, today=False):
    """Lister les rendez-vous d'un médecin (par medecin_id)"""
    with get_cursor() as (conn, cur):
        if today:
            today_date = date.today()
            query = """
                SELECT r.*, 
                       p.nom as patient_nom, 
                       p.prenom as patient_prenom,
                       p.telephone as patient_telephone
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                WHERE r.medecin_id = %s AND DATE(r.date_heure) = %s
                ORDER BY r.date_heure ASC
            """
            cur.execute(query, (medecin_id, today_date))
        else:
            query = """
                SELECT r.*, 
                       p.nom as patient_nom, 
                       p.prenom as patient_prenom,
                       p.telephone as patient_telephone
                FROM rendezvous r
                JOIN patients p ON r.patient_id = p.id
                WHERE r.medecin_id = %s
                ORDER BY r.date_heure DESC
            """
            cur.execute(query, (medecin_id,))
        
        rows = cur.fetchall()
        return [_row_to_rdv(r) for r in rows if r]

# ----------------- GET SINGLE -----------------
def get_rdv(rdv_id, medecin_id):
    """Récupérer un rendez-vous spécifique"""
    with get_cursor() as (conn, cur):
        query = """
            SELECT r.*, 
                   p.nom as patient_nom, 
                   p.prenom as patient_prenom,
                   p.telephone as patient_telephone
            FROM rendezvous r
            JOIN patients p ON r.patient_id = p.id
            WHERE r.id = %s AND r.medecin_id = %s
        """
        cur.execute(query, (rdv_id, medecin_id))
        row = cur.fetchone()
        return _row_to_rdv(row)

# ----------------- CREATE -----------------
def create_rdv(payload):
    """Créer un nouveau rendez-vous"""
    with get_cursor() as (conn, cur):
        # Formater la date si nécessaire
        date_heure = payload['date_heure']
        if 'T' in date_heure:
            # Convertir du format HTML datetime-local au format MySQL
            date_heure = date_heure.replace('T', ' ')
        if date_heure.endswith('Z'):
            date_heure = date_heure[:-1]
        
        # Vérifier que le créneau n'est pas déjà pris
        check_query = """
            SELECT id FROM rendezvous 
            WHERE medecin_id = %s AND date_heure = %s
        """
        cur.execute(check_query, (payload['medecin_id'], date_heure))
        existing = cur.fetchone()
        
        if existing:
            raise Exception("Ce créneau est déjà réservé pour ce médecin")
        
        # Insérer le nouveau rendez-vous
        query = """
            INSERT INTO rendezvous (patient_id, medecin_id, date_heure, statut, notes)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (
            payload['patient_id'],
            payload['medecin_id'],
            date_heure,
            payload.get('statut', 'En attente'),
            payload.get('notes', '')
        ))
        
        # Récupérer le rendez-vous créé
        rdv_id = cur.lastrowid
        
        # Retourner les données complètes
        query = """
            SELECT r.*, 
                   p.nom as patient_nom, 
                   p.prenom as patient_prenom,
                   p.telephone as patient_telephone
            FROM rendezvous r
            JOIN patients p ON r.patient_id = p.id
            WHERE r.id = %s
        """
        cur.execute(query, (rdv_id,))
        row = cur.fetchone()
        
        return _row_to_rdv(row)

# ----------------- UPDATE -----------------
def update_rdv(rdv_id, medecin_id, payload):
    """Mettre à jour un rendez-vous"""
    with get_cursor() as (conn, cur):
        # Vérifier que le rendez-vous existe et appartient au médecin
        check_query = """
            SELECT id FROM rendezvous 
            WHERE id = %s AND medecin_id = %s
        """
        cur.execute(check_query, (rdv_id, medecin_id))
        if not cur.fetchone():
            return None
        
        # Formater la date si présente dans le payload
        if 'date_heure' in payload:
            date_heure = payload['date_heure']
            if 'T' in date_heure:
                date_heure = date_heure.replace('T', ' ')
            if date_heure.endswith('Z'):
                date_heure = date_heure[:-1]
            payload['date_heure'] = date_heure
            
            # Vérifier que la nouvelle date n'est pas déjà prise
            check_date_query = """
                SELECT id FROM rendezvous 
                WHERE medecin_id = %s 
                AND date_heure = %s 
                AND id != %s
            """
            cur.execute(check_date_query, (medecin_id, date_heure, rdv_id))
            existing = cur.fetchone()
            
            if existing:
                raise Exception("Ce créneau est déjà réservé pour ce médecin")
        
        # Construire la requête de mise à jour
        allowed_fields = ['patient_id', 'date_heure', 'statut', 'notes']
        updates = []
        params = []
        
        for field in allowed_fields:
            if field in payload:
                updates.append(f"{field} = %s")
                params.append(payload[field])
        
        if not updates:
            # Pas de modifications, retourner les données actuelles
            return get_rdv(rdv_id, medecin_id)
        
        params.extend([rdv_id, medecin_id])
        query = f"UPDATE rendezvous SET {', '.join(updates)} WHERE id = %s AND medecin_id = %s"
        
        cur.execute(query, tuple(params))
        
        # Retourner les données mises à jour
        return get_rdv(rdv_id, medecin_id)

# ----------------- DELETE -----------------
def delete_rdv(rdv_id, medecin_id):
    """Supprimer un rendez-vous"""
    with get_cursor() as (conn, cur):
        # Vérifier que le rendez-vous existe et appartient au médecin
        check_query = """
            SELECT id FROM rendezvous 
            WHERE id = %s AND medecin_id = %s
        """
        cur.execute(check_query, (rdv_id, medecin_id))
        if not cur.fetchone():
            return False
        
        # Supprimer le rendez-vous (avec vérification du medecin_id pour plus de sécurité)
        delete_query = "DELETE FROM rendezvous WHERE id = %s AND medecin_id = %s"
        cur.execute(delete_query, (rdv_id, medecin_id))
        
        return cur.rowcount > 0

# Fonction supplémentaire pour vérifier la disponibilité
def check_disponibilite(medecin_id, date_heure):
    """Vérifier si un créneau est disponible pour un médecin"""
    with get_cursor() as (conn, cur):
        # Formater la date si nécessaire
        if 'T' in date_heure:
            date_heure = date_heure.replace('T', ' ')
        if date_heure.endswith('Z'):
            date_heure = date_heure[:-1]
            
        query = """
            SELECT id FROM rendezvous 
            WHERE medecin_id = %s AND date_heure = %s
        """
        cur.execute(query, (medecin_id, date_heure))
        existing = cur.fetchone()
        
        return existing is None  # True si disponible, False si déjà pris

# Fonction pour récupérer les statistiques
def get_stats(medecin_id):
    """Récupérer les statistiques des rendez-vous pour un médecin"""
    with get_cursor() as (conn, cur):
        query = """
            SELECT 
                statut,
                COUNT(*) as count
            FROM rendezvous
            WHERE medecin_id = %s
            GROUP BY statut
        """
        cur.execute(query, (medecin_id,))
        rows = cur.fetchall()
        
        stats = {row['statut']: row['count'] for row in rows}
        
        # Calculer le total
        total = sum(stats.values())
        
        return {
            'total': total,
            'par_statut': stats
        }

# Fonction pour vérifier si le médecin existe
def medecin_exists(medecin_id):
    """Vérifier si un médecin existe dans la table medecins"""
    with get_cursor() as (conn, cur):
        query = "SELECT id FROM medecins WHERE id = %s"
        cur.execute(query, (medecin_id,))
        result = cur.fetchone()
        return result is not None