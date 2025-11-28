from flask import Blueprint, render_template,request,jsonify
from app import get_db_connection
patient = Blueprint("patient", __name__, url_prefix="/patient")

@patient.route("/accueil")
def accueil():
    return render_template("patient/accueil.html")

@patient.route("/dashboard")
def dashboard():
    return render_template("patient/dashboard.html")

@patient.route("/mes_rdv")
def mes_rdv():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom FROM specialisations")
    specialisations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("patient/mes_rdv.html", specialisations=specialisations)
 

@patient.route("/profile")
def profile():
    return render_template("patient/profile.html")

@patient.route("/logout")
def logout():
    return render_template("patient/logout.html")

@patient.route("/prise_rdv")
def prise_rdv():
    return render_template("patient/prise_rdv.html")
   
@patient.route("/get_doctors")
def get_doctors():
    specialization_id = request.args.get('specialization')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Requête pour récupérer les docteurs de cette spécialisation
    cursor.execute("""
        SELECT id, nom 
        FROM medecins
        WHERE id_specialisation = %s
    """, (specialization_id,))
    
    docteurs = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print(f"Docteurs pour spécialisation {specialization_id}:", docteurs)  # Débogage
    
    # Retourner en JSON
    return jsonify([{
        "id": d[0], 
        "nom": f"{d[1]}"  # Nom complet
    } for d in docteurs])
#creer route honoraire
@patient.route("/get_honoraires")
def get_honoraires():
    doctor_id = request.args.get('doctor_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer l'honoraire du médecin
    cursor.execute("""
        SELECT id, tarif_consultation 
        FROM medecins
        WHERE id = %s
    """, (doctor_id,))
    
    medecin = cursor.fetchone()
    cursor.close()
    conn.close()
    
    print(f"Honoraire pour docteur {doctor_id}:", medecin)  # Débogage
    
    # Retourner en JSON (un seul honoraire)
    if medecin:
        return jsonify([{
            "id": medecin[0], 
            "montant": medecin[1]
        }])
    else:
        return jsonify([])