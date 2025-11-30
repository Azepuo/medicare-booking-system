import mysql.connector
import bcrypt

# -----------------------
# Seed principal
# -----------------------
def seed_all(cursor):
    seed_patients(cursor)
    seed_medecins(cursor)
    seed_admins(cursor)
    seed_disponibilites(cursor)
    seed_rendezvous(cursor)
    seed_avis(cursor)
    seed_statistiques(cursor)
    print("Toutes les données insérées avec succès.")

# -----------------------
# Patients
# -----------------------
def seed_patients(cursor):
    patients = [
        ("Yassine El Amrani", "yassine.elamrani@gmail.com", "0612345678", "MotDePasse123"),
        ("Khadija Benali", "khadija.benali@gmail.com", "0678123456", "Pass456"),
        ("Omar Essafi", "omar.essafi@gmail.com", "0655332211", "Secret789"),
        ("Fatima Zahra Lahrichi", "fatima.lahrichi@gmail.com", "0666778899", "Pwd1234"),
    ]
    for nom, email, telephone, password in patients:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cursor.execute("""
            INSERT INTO patients (nom, email, telephone, password, date_inscription)
            VALUES (%s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE telephone=%s, password=%s
        """, (nom, email, telephone, hashed_password, telephone, hashed_password))
    print("Patients insérés.")

# -----------------------
# Médecins
# -----------------------
def seed_medecins(cursor):
    medecins = [
        ("Dr. Rachid El Idrissi", "Cardiologie", "rachid.elidrissi@clinique.ma", "Spécialiste maladies cardiovasculaires", 10, 300, "MedPass1"),
        ("Dr. Salma Berrada", "Dermatologie", "salma.berrada@clinique.ma", "Traitement affections cutanées", 8, 250, "MedPass2"),
        ("Dr. Youssef Amrani", "Pédiatrie", "youssef.amrani@hopital.ma", "Santé infantile", 6, 220, "MedPass3"),
    ]
    for nom, specialite, email, description, annees_exp, tarif, password in medecins:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cursor.execute("""
            INSERT INTO medecins (nom, specialite, email, description, annees_experience, tarif_consultation, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE tarif_consultation=%s, password=%s
        """, (nom, specialite, email, description, annees_exp, tarif, hashed_password, tarif, hashed_password))
    print("Médecins insérés.")

# -----------------------
# Admins
# -----------------------
def seed_admins(cursor):
    admins = [
        ("Admin Super", "admin@clinique.ma", "AdminPass123")
    ]
    for nom, email, password in admins:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cursor.execute("""
            INSERT INTO admins (nom, email, password, date_inscription)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE password=%s
        """, (nom, email, hashed_password, hashed_password))
    print("Admins insérés.")

# -----------------------
# Disponibilités
# -----------------------
def seed_disponibilites(cursor):
    disponibilites = [
        (1, "Lundi", "09:00", "12:00"),
        (1, "Jeudi", "14:00", "17:00"),
        (2, "Mardi", "10:00", "13:00"),
    ]
    for medecin_id, jour, debut, fin in disponibilites:
        cursor.execute("""
            INSERT INTO disponibilites (medecin_id, jour_semaine, heure_debut, heure_fin)
            VALUES (%s, %s, %s, %s)
        """, (medecin_id, jour, debut, fin))
    print("Disponibilités insérées.")

# -----------------------
# Rendez-vous
# -----------------------
def seed_rendezvous(cursor):
    rdvs = [
        ("2025-11-10 10:00:00", 1, 1, "Confirmé", "Consultation annuelle"),
        ("2025-11-11 11:30:00", 2, 2, "Confirmé", "Traitement dermatologique"),
    ]
    for date_heure, patient_id, medecin_id, statut, notes in rdvs:
        cursor.execute("""
            INSERT INTO rendezvous (date_heure, patient_id, medecin_id, statut, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (date_heure, patient_id, medecin_id, statut, notes))
    print("Rendez-vous insérés.")

# -----------------------
# Avis
# -----------------------
def seed_avis(cursor):
    avis = [
        (1, 1, 5, "Très bon suivi"),
        (2, 2, 4, "Bon accueil"),
    ]
    for patient_id, medecin_id, note, commentaire in avis:
        cursor.execute("""
            INSERT INTO avis (patient_id, medecin_id, note, commentaire)
            VALUES (%s, %s, %s, %s)
        """, (patient_id, medecin_id, note, commentaire))
    print("Avis insérés.")

# -----------------------
# Statistiques
# -----------------------
def seed_statistiques(cursor):
    stats = [
        (1, 120, 85, 40, 4.7),
        (2, 95, 70, 35, 4.4),
    ]
    for medecin_id, total_rdv, total_patients, total_avis, moyenne in stats:
        cursor.execute("""
            INSERT INTO statistiques (medecin_id, total_rdv, total_patients, total_avis, moyenne_notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (medecin_id, total_rdv, total_patients, total_avis, moyenne))
    print("Statistiques insérées.")

