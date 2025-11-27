# app/rpc_medecin/rdv_rpc_methods.py
from datetime import datetime, date
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    """Créer une connexion à la base de données"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '3306'),
            database=os.getenv('DB_NAME', 'medicare_booking'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        return conn
    except Error as e:
        print(f"Erreur de connexion à la base: {e}")
        return None

def list_all_rdv():
    """Liste tous les rendez-vous"""
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT r.id, r.date_heure, r.notes, r.statut,
               p.nom, p.prenom, p.telephone, p.email
        FROM rendez_vous r
        LEFT JOIN patients p ON r.patient_id = p.id
        ORDER BY r.date_heure DESC
        """
        cursor.execute(query)
        rdvs = cursor.fetchall()
        
        result = []
        for rdv in rdvs:
            result.append({
                'id': rdv['id'],
                'patient_nom': f"{rdv['prenom']} {rdv['nom']}" if rdv['prenom'] and rdv['nom'] else 'N/A',
                'patient_telephone': rdv['telephone'] or 'N/A',
                'date_heure': rdv['date_heure'].strftime('%Y-%m-%d %H:%M:%S') if rdv['date_heure'] else '',
                'notes': rdv['notes'] or '',
                'statut': rdv['statut'] or 'En attente'
            })
        return result
    except Error as e:
        print(f"Erreur list_all_rdv: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def list_today_rdv():
    """Liste les rendez-vous d'aujourd'hui"""
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT r.id, r.date_heure, r.notes, r.statut,
               p.nom, p.prenom, p.telephone, p.email
        FROM rendez_vous r
        LEFT JOIN patients p ON r.patient_id = p.id
        WHERE DATE(r.date_heure) = CURDATE()
        ORDER BY r.date_heure ASC
        """
        cursor.execute(query)
        rdvs = cursor.fetchall()
        
        result = []
        for rdv in rdvs:
            result.append({
                'id': rdv['id'],
                'patient_nom': f"{rdv['prenom']} {rdv['nom']}" if rdv['prenom'] and rdv['nom'] else 'N/A',
                'patient_telephone': rdv['telephone'] or 'N/A',
                'date_heure': rdv['date_heure'].strftime('%H:%M') if rdv['date_heure'] else '',
                'notes': rdv['notes'] or '',
                'statut': rdv['statut'] or 'En attente'
            })
        return result
    except Error as e:
        print(f"Erreur list_today_rdv: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_rdv(rid):
    conn = create_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT r.id, r.patient_id, r.date_heure, r.notes, r.statut,
               p.nom, p.prenom, p.telephone
        FROM rendez_vous r
        LEFT JOIN patients p ON r.patient_id = p.id
        WHERE r.id = %s
        """
        cursor.execute(query, (rid,))
        rdv = cursor.fetchone()
        
        if rdv:
            return {
                'id': rdv['id'],
                'patient_id': rdv['patient_id'],
                'patient_nom': f"{rdv['prenom']} {rdv['nom']}" if rdv['prenom'] and rdv['nom'] else 'N/A',
                'date_heure': rdv['date_heure'].strftime('%Y-%m-%d %H:%M:%S') if rdv['date_heure'] else '',
                'notes': rdv['notes'] or '',
                'statut': rdv['statut'] or 'En attente'
            }
        return None
    except Error as e:
        print(f"Erreur get_rdv: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def create_rdv(data):
    conn = create_connection()
    if not conn:
        raise Exception("Impossible de se connecter à la base de données")
    
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO rendez_vous (patient_id, date_heure, notes, statut)
        VALUES (%s, %s, %s, %s)
        """
        values = (
            data.get('patient_id'),
            data.get('date_heure'),
            data.get('notes', ''),
            data.get('statut', 'En attente')
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        return {
            'id': cursor.lastrowid,
            'success': True
        }
    except Error as e:
        conn.rollback()
        raise Exception(f"Erreur création RDV: {e}")
    finally:
        cursor.close()
        conn.close()

def update_rdv(rid, data):
    conn = create_connection()
    if not conn:
        raise Exception("Impossible de se connecter à la base de données")
    
    try:
        cursor = conn.cursor()
        
        # Vérifier si le RDV existe
        check_query = "SELECT id FROM rendez_vous WHERE id = %s"
        cursor.execute(check_query, (rid,))
        if not cursor.fetchone():
            raise Exception("Rendez-vous non trouvé")
        
        # Construire la requête de mise à jour dynamiquement
        update_fields = []
        values = []
        
        if 'date_heure' in data:
            update_fields.append("date_heure = %s")
            values.append(data['date_heure'])
        if 'notes' in data:
            update_fields.append("notes = %s")
            values.append(data['notes'])
        if 'statut' in data:
            update_fields.append("statut = %s")
            values.append(data['statut'])
        
        if not update_fields:
            raise Exception("Aucune donnée à mettre à jour")
        
        values.append(rid)
        query = f"UPDATE rendez_vous SET {', '.join(update_fields)} WHERE id = %s"
        
        cursor.execute(query, values)
        conn.commit()
        
        return {
            'id': rid,
            'success': True
        }
    except Error as e:
        conn.rollback()
        raise Exception(f"Erreur mise à jour RDV: {e}")
    finally:
        cursor.close()
        conn.close()

def delete_rdv(rid):
    conn = create_connection()
    if not conn:
        raise Exception("Impossible de se connecter à la base de données")
    
    try:
        cursor = conn.cursor()
        
        # Vérifier si le RDV existe
        check_query = "SELECT id FROM rendez_vous WHERE id = %s"
        cursor.execute(check_query, (rid,))
        if not cursor.fetchone():
            return False
        
        delete_query = "DELETE FROM rendez_vous WHERE id = %s"
        cursor.execute(delete_query, (rid,))
        conn.commit()
        
        return cursor.rowcount > 0
    except Error as e:
        conn.rollback()
        raise Exception(f"Erreur suppression RDV: {e}")
    finally:
        cursor.close()
        conn.close()