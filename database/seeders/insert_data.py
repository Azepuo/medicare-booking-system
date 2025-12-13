# database/seeders/insert_data.py

import bcrypt

DEFAULT_PASSWORD = "Pass1234"

def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def seed_all(cursor):
    seed_admins(cursor)
def seed_all(cursor):
    seed_patients(cursor)
    seed_medecins(cursor)
    seed_disponibilites(cursor)
    seed_rendezvous(cursor)
    seed_avis(cursor)
    seed_statistiques(cursor)
    print("Données marocaines insérées avec succès.")



# NOUVEAU : Insérer l'Admin
def seed_admins(cursor):
    # Mot de passe haché pour 'admin@clinique.ma'
    hashed_pass = hash_password(DEFAULT_PASSWORD) 
    
    admins = [
        ("Super Admin", "admin@clinique.ma", hashed_pass, "0537000000"),
    ]
    for nom, email, password, tel in admins:
        cursor.execute("""
            INSERT INTO admins (nom, email, password, telephone) 
            VALUES (%s, %s, %s, %s)
        """, (nom, email, password, tel))
    print("Admin inséré.")


# Patients marocains
def seed_patients(cursor):
    patients = [
        ("Yassine El Amrani", "yassine.elamrani@gmail.com", "0612345678"),
        ("Khadija Benali", "khadija.benali@gmail.com", "0678123456"),
        ("Omar Essafi", "omar.essafi@gmail.com", "0655332211"),
        ("Fatima Zahra Lahrichi", "fatima.lahrichi@gmail.com", "0666778899"),
        ("Ahmed Bouzid", "ahmed.bouzid@gmail.com", "0622334455"),
        ("Hajar El Gharbi", "hajar.elgharbi@gmail.com", "0688997766"),
        ("Mohamed Ait Taleb", "mohamed.aittaleb@gmail.com", "0655123499"),
        ("Sara Mansouri", "sara.mansouri@gmail.com", "0677112233"),
        ("Soufiane Chafai", "soufiane.chafai@gmail.com", "0699887766"),
        ("Rania Azzouz", "rania.azzouz@gmail.com", "0611998877"),
        ("Zakaria Lamrabet", "zakaria.lamrabet@gmail.com", "0622113344"),
        ("Houssam Idrissi", "houssam.idrissi@gmail.com", "0677558899"),
        ("Nawal Tahiri", "nawal.tahiri@gmail.com", "0688114455"),
        ("Hamza El Khatib", "hamza.elkhatib@gmail.com", "0666112288"),
        ("Meryem Kabbaj", "meryem.kabbaj@gmail.com", "0699554433"),
        ("Imane Bouziane", "imane.bouziane@gmail.com", "0688001122"),
        ("Khalid Rami", "khalid.rami@gmail.com", "0677445566"),
        ("Souad Achraf", "souad.achraf@gmail.com", "0622447788"),
        ("Abdelhak El Fassi", "abdelhak.elfassi@gmail.com", "0666223344"),
        ("Amina El Mansouri", "amina.elmansouri@gmail.com", "0655889911")
    ]
    for nom, email, tel in patients:
        cursor.execute("INSERT INTO patients (nom, email, telephone) VALUES (%s, %s, %s)", (nom, email, tel))
    print("Patients marocains insérés.")


# Médecins marocains
def seed_medecins(cursor):
    medecins = [
        ("Dr. Rachid El Idrissi", "Cardiologie", "rachid.elidrissi@clinique.ma", "Spécialiste en maladies cardiovasculaires à Marrakech.", 300),
        ("Dr. Salma Berrada", "Dermatologie", "salma.berrada@clinique.ma", "Traitement des affections cutanées et esthétiques.", 250),
        ("Dr. Youssef Amrani", "Pédiatrie", "youssef.amrani@hopital.ma", "Spécialiste en santé infantile à Casablanca.", 220),
        ("Dr. Souad Fassi", "Gynécologie", "souad.fassi@clinique.ma", "Suivi prénatal et santé de la femme.", 280),
        ("Dr. Hamza Ait Taleb", "Médecine Générale", "hamza.aittaleb@cabinet.ma", "Médecin généraliste expérimenté à Agadir.", 180),
        ("Dr. Sara Kabbaj", "Ophtalmologie", "sara.kabbaj@clinique.ma", "Spécialiste de la vue et des troubles oculaires.", 270),
        ("Dr. Mehdi Bouchaib", "Neurologie", "mehdi.bouchaib@hopital.ma", "Suivi des maladies du système nerveux.", 320),
        ("Dr. Hicham El Hadi", "Orthopédie", "hicham.elhadi@hopital.ma", "Spécialiste des os et articulations.", 310),
        ("Dr. Kawtar El Othmani", "Endocrinologie", "kawtar.elothmani@clinique.ma", "Diabète, thyroïde et métabolisme.", 290),
        ("Dr. Rachida Bensalem", "Psychiatrie", "rachida.bensalem@hopital.ma", "Consultation et thérapie psychologique.", 300)
    ]
    for nom, specialite, email, description, tarif in medecins:
        cursor.execute("""
            INSERT INTO medecins (nom, specialite, email, description, tarif_consultation)
            VALUES (%s, %s, %s, %s, %s)
        """, (nom, specialite, email, description, tarif))
    print("Médecins marocains insérés.")


# Disponibilités
def seed_disponibilites(cursor):
    disponibilites = [
        (1, "Lundi", "09:00", "12:00"),
        (1, "Jeudi", "14:00", "17:00"),
        (2, "Mardi", "10:00", "13:00"),
        (3, "Mercredi", "09:00", "12:00"),
        (4, "Vendredi", "10:00", "13:30"),
        (5, "Samedi", "09:00", "11:30"),
        (6, "Lundi", "15:00", "18:00"),
        (7, "Mardi", "09:00", "12:00"),
        (8, "Jeudi", "10:00", "13:00"),
        (9, "Mercredi", "08:30", "12:30"),
        (10, "Vendredi", "14:00", "17:00")
    ]
    for medecin_id, jour, debut, fin in disponibilites:
        cursor.execute("""
            INSERT INTO disponibilites (medecin_id, jour_semaine, heure_debut, heure_fin)
            VALUES (%s, %s, %s, %s)
        """, (medecin_id, jour, debut, fin))
    print("Disponibilités insérées.")


# Rendez-vous
def seed_rendezvous(cursor):
    rdvs = [
        ("2025-11-10 10:00:00", 1, 1, "Confirmé", "Consultation annuelle."),
        ("2025-11-11 11:30:00", 2, 2, "Confirmé", "Traitement dermatologique."),
        ("2025-11-12 09:00:00", 3, 3, "En attente", "Vaccination enfant."),
        ("2025-11-13 14:00:00", 4, 4, "Confirmé", "Suivi gynécologique."),
        ("2025-11-14 16:00:00", 5, 5, "Annulé", "Consultation générale."),
        ("2025-11-15 11:00:00", 6, 6, "Confirmé", "Contrôle de la vue."),
        ("2025-11-16 10:30:00", 7, 7, "Confirmé", "Consultation neurologique."),
        ("2025-11-17 12:00:00", 8, 8, "En attente", "Douleur à la jambe."),
        ("2025-11-18 09:30:00", 9, 9, "Confirmé", "Suivi thyroïde."),
        ("2025-11-19 15:00:00", 10, 10, "Confirmé", "Consultation psychologique.")
    ]
    for date_heure, patient, medecin, statut, notes in rdvs:
        cursor.execute("""
            INSERT INTO rendezvous (date_heure, patient_id, medecin_id, statut, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (date_heure, patient, medecin, statut, notes))
    print("Rendez-vous insérés.")


# Avis
def seed_avis(cursor):
    avis = [
        (1, 1, 5, "Médecin très compétent et à l’écoute."),
        (2, 2, 4, "Bon accueil et explications claires."),
        (3, 3, 5, "Très bon suivi pour les enfants."),
        (4, 4, 4, "Service professionnel."),
        (5, 5, 3, "Délai d’attente un peu long."),
        (6, 6, 5, "Excellent ophtalmologue."),
        (7, 7, 4, "Expérience positive."),
        (8, 8, 5, "Traitement efficace."),
        (9, 9, 4, "Très bon suivi médical."),
        (10, 10, 5, "Très compréhensive et à l’écoute.")
    ]
    for patient, medecin, note, commentaire in avis:
        cursor.execute("""
            INSERT INTO avis (patient_id, medecin_id, note, commentaire)
            VALUES (%s, %s, %s, %s)
        """, (patient, medecin, note, commentaire))
    print("Avis insérés.")


# Statistiques
def seed_statistiques(cursor):
    stats = [
        (1, 120, 85, 40, 4.7),
        (2, 95, 70, 35, 4.4),
        (3, 80, 65, 25, 4.8),
        (4, 60, 50, 20, 4.1),
        (5, 130, 100, 50, 4.6),
        (6, 75, 60, 22, 4.5),
        (7, 55, 48, 15, 4.3),
        (8, 90, 70, 30, 4.6),
        (9, 85, 75, 32, 4.5),
        (10, 100, 80, 40, 4.9)
    ]
    for medecin, total_rdv, total_patients, total_avis, moyenne in stats:
        cursor.execute("""
            INSERT INTO statistiques (medecin_id, total_rdv, total_patients, total_avis, moyenne_notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (medecin, total_rdv, total_patients, total_avis, moyenne))
    print("Statistiques insérées.")
