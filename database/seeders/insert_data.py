# database/seeders/insert_data.py

def seed_all(cursor):
    seed_patients(cursor)
    seed_medecins(cursor)
    seed_disponibilites(cursor)
    seed_rendezvous(cursor)
    seed_avis(cursor)
    seed_statistiques(cursor)
    print("🌿 Données insérées avec succès !")

def seed_patients(cursor):
    patients = [
        ("Jean Dupont", "jean@example.com", "0611223344"),
        ("Marie Curie", "marie@example.com", "0622334455"),
        ("Ali Ben", "ali@example.com", "0677889900"),
        ("Sarah B.", "sarah@example.com", "0655443322")
    ]
    for nom, email, tel in patients:
        cursor.execute("INSERT INTO patients (nom, email, telephone) VALUES (%s, %s, %s)", (nom, email, tel))
    print("👤 Patients insérés.")

def seed_medecins(cursor):
    medecins = [
        ("Dr. Martin", "Cardiologie", "martin@hopital.com", "15 ans d’expérience", 250),
        ("Dr. Dupont", "Dermatologie", "dupont@hopital.com", "10 ans d’expérience", 200),
        ("Dr. Nadia", "Pédiatrie", "nadia@hopital.com", "12 ans d’expérience", 220)
    ]
    for nom, specialite, email, description, tarif in medecins:
        cursor.execute("""
            INSERT INTO medecins (nom, specialite, email, description, tarif_consultation)
            VALUES (%s, %s, %s, %s, %s)
        """, (nom, specialite, email, description, tarif))
    print("🩺 Médecins insérés.")

def seed_disponibilites(cursor):
    disponibilites = [
        (1, "Lundi", "09:00", "12:00"),
        (1, "Mardi", "14:00", "18:00"),
        (2, "Mercredi", "09:00", "12:30"),
        (3, "Jeudi", "10:00", "13:00")
    ]
    for medecin_id, jour, debut, fin in disponibilites:
        cursor.execute("""
            INSERT INTO disponibilites (medecin_id, jour_semaine, heure_debut, heure_fin)
            VALUES (%s, %s, %s, %s)
        """, (medecin_id, jour, debut, fin))
    print("🕒 Disponibilités insérées.")

def seed_rendezvous(cursor):
    rdvs = [
        ("2025-11-10 10:00:00", 1, 1, "Confirmé", "Suivi annuel"),
        ("2025-11-11 15:30:00", 2, 2, "En attente", "Première consultation"),
        ("2025-11-12 11:00:00", 3, 3, "Annulé", "Conflit de planning")
    ]
    for date_heure, patient, medecin, statut, notes in rdvs:
        cursor.execute("""
            INSERT INTO rendezvous (date_heure, patient_id, medecin_id, statut, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (date_heure, patient, medecin, statut, notes))
    print("📅 Rendez-vous insérés.")

def seed_avis(cursor):
    avis = [
        (1, 1, 5, "Excellent médecin."),
        (2, 2, 4, "Bon diagnostic."),
        (3, 3, 3, "Correct mais rapide.")
    ]
    for patient, medecin, note, commentaire in avis:
        cursor.execute("""
            INSERT INTO avis (patient_id, medecin_id, note, commentaire)
            VALUES (%s, %s, %s, %s)
        """, (patient, medecin, note, commentaire))
    print("💬 Avis insérés.")

def seed_statistiques(cursor):
    stats = [
        (1, 30, 20, 10, 4.8),
        (2, 25, 18, 9, 4.4),
        (3, 15, 12, 6, 3.9)
    ]
    for medecin, total_rdv, total_patients, total_avis, moyenne in stats:
        cursor.execute("""
            INSERT INTO statistiques (medecin_id, total_rdv, total_patients, total_avis, moyenne_notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (medecin, total_rdv, total_patients, total_avis, moyenne))
    print("📊 Statistiques insérées.")
