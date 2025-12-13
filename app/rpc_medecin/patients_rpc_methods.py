# app/rpc_medecin/patients_rpc_methods.py
from database.connection_m import create_connection
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from datetime import datetime

# ----------------- CONTEXT MANAGER -----------------
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

# ----------------- HELPERS -----------------
def _row_to_patient(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not row:
        return None
    
    # Formater date_inscription en ISO
    if 'date_inscription' in row and isinstance(row['date_inscription'], datetime):
        row['date_inscription'] = row['date_inscription'].strftime('%Y-%m-%d %H:%M:%S')
    
    # S'assurer que tous les champs nécessaires existent
    result = {
        'id': row.get('id'),
        'nom': row.get('nom', ''),
        'email': row.get('email', ''),
        'telephone': row.get('telephone', ''),
        'age': row.get('age'),
        'date_inscription': row.get('date_inscription', '')
    }
    return result

# ----------------- LIST -----------------
def list_patients() -> List[Dict[str, Any]]:
    with get_cursor() as (conn, cur):
        cur.execute("SELECT * FROM patients ORDER BY date_inscription DESC")
        rows = cur.fetchall()
        return [_row_to_patient(r) for r in rows if r]

# ----------------- GET SINGLE -----------------
def get_patient(pid: int) -> Optional[Dict[str, Any]]:
    with get_cursor() as (conn, cur):
        cur.execute("SELECT * FROM patients WHERE id=%s", (pid,))
        row = cur.fetchone()
        return _row_to_patient(row)

# ----------------- CREATE -----------------
def create_patient(payload: Dict[str, Any]) -> Dict[str, Any]:
    nom = payload.get('nom')
    email = payload.get('email')
    telephone = payload.get('telephone', '')
    age = payload.get('age', None)

    if not nom or not email:
        raise ValueError("Nom et email sont requis")

    sql = "INSERT INTO patients (nom, email, telephone, age) VALUES (%s, %s, %s, %s)"
    with get_cursor() as (conn, cur):
        cur.execute(sql, (nom, email, telephone, age))
        new_id = cur.lastrowid
        cur.execute("SELECT * FROM patients WHERE id=%s", (new_id,))
        row = cur.fetchone()
        return _row_to_patient(row)

# ----------------- UPDATE -----------------
def update_patient(pid: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    allowed = ["nom", "email", "telephone", "age"]
    sets = []
    params = []
    for field in allowed:
        if field in data:
            sets.append(f"{field}=%s")
            params.append(data[field])
    if not sets:
        return get_patient(pid)
    params.append(pid)
    sql = "UPDATE patients SET " + ", ".join(sets) + " WHERE id=%s"
    with get_cursor() as (conn, cur):
        cur.execute(sql, tuple(params))
        cur.execute("SELECT * FROM patients WHERE id=%s", (pid,))
        row = cur.fetchone()
        return _row_to_patient(row)

# ----------------- DELETE -----------------
def delete_patient(pid: int) -> bool:
    with get_cursor() as (conn, cur):
        cur.execute("SELECT 1 FROM patients WHERE id=%s", (pid,))
        if not cur.fetchone():
            return False
        cur.execute("DELETE FROM patients WHERE id=%s", (pid,))
        return True