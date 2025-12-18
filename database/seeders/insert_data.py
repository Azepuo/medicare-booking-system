# database/seeders/insert_data.py

from werkzeug.security import generate_password_hash
import bcrypt

DEFAULT_PASSWORD = "Pass1234"
DEFAULT_MEDECIN_PASSWORD = "Medecin1234"

def seed_all(connection, cursor):
    seed_admins(connection, cursor)
    seed_patients(connection, cursor)
    seed_medecins(connection, cursor)
    seed_disponibilites(connection, cursor)
    seed_rendezvous(connection, cursor)
    seed_avis(connection, cursor)
    seed_statistiques(connection, cursor)
    print("Données marocaines insérées avec succès.")


# ================= Admin =================
def seed_admins(connection, cursor):
    hashed_pass = generate_password_hash(DEFAULT_PASSWORD, method="pbkdf2:sha256")

    admins = [
        ("Super Admin", "admin1@clinique.ma", hashed_pass, "0537000000"),
    ]

    for nom, email, password, tel in admins:
        cursor.execute("""
            INSERT INTO admins (nom, email, password, telephone)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            password = VALUES(password)  -- ici tu peux choisir de mettre à jour le mot de passe
        """, (nom, email, password, tel))

    connection.commit()
    print("Admin inséré ou déjà existant ignoré.")



# ================= Patients =================
def seed_patients(connection, cursor):
    patients = [
        ("Yassine El Amrani", "y.elamrani@gmail.com", "0612345678"),
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
        cursor.execute("""
            INSERT INTO patients (nom, email, telephone)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            nom = nom  -- ne change rien, juste pour éviter l'erreur
            """, (nom, email, tel))


    connection.commit()
    print("Patients marocains insérés.")


# ================= Médecins =================

from werkzeug.security import generate_password_hash, check_password_hash

hashed = generate_password_hash("Medecin1234")
check_password_hash(hashed, "Medecin1234")

def seed_medecins(connection, cursor):
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
        hashed_pass = generate_password_hash(DEFAULT_PASSWORD, method="pbkdf2:sha256")
        cursor.execute("""
            INSERT INTO medecins (nom, specialite, email, description, tarif_consultation, password)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            specialite = VALUES(specialite),
            description = VALUES(description),
            tarif_consultation = VALUES(tarif_consultation)
        """, (nom, specialite, email, description, tarif, hashed_pass))

    connection.commit()
    print("Médecins marocains insérés ou mis à jour.")


# ================= Disponibilités =================
def seed_disponibilites(connection, cursor):
    disponibilites = [
        (42, "Lundi", "09:00", "12:00"),
        (43, "Jeudi", "14:00", "17:00"),
        (44, "Mardi", "10:00", "13:00"),
        (45, "Mercredi", "09:00", "12:00"),
        (46, "Vendredi", "10:00", "13:30"),
        (47, "Samedi", "09:00", "11:30"),
        (48, "Lundi", "15:00", "18:00"),
        (49, "Mardi", "09:00", "12:00"),
        (50, "Jeudi", "10:00", "13:00"),
        (51, "Mercredi", "08:30", "12:30"),
    ]

    for medecin_id, jour, debut, fin in disponibilites:
        cursor.execute("""
            INSERT INTO disponibilites (medecin_id, jour_semaine, heure_debut, heure_fin)
            VALUES (%s, %s, %s, %s)
        """, (medecin_id, jour, debut, fin))

    connection.commit()
    print("Disponibilités insérées.")


# ================= Rendez-vous =================
def seed_rendezvous(connection, cursor):
    rdvs = [
        ("2025-11-10 10:00:00", 1, 42, "Confirmé", "Consultation annuelle."),
        ("2025-11-11 11:30:00", 2, 43, "Confirmé", "Traitement dermatologique."),
        ("2025-11-12 09:00:00", 3, 44, "En attente", "Vaccination enfant."),
        ("2025-11-13 14:00:00", 4, 45, "Confirmé", "Suivi gynécologique."),
        ("2025-11-14 16:00:00", 5, 46, "Annulé", "Consultation générale."),
        ("2025-11-15 11:00:00", 6, 47, "Confirmé", "Contrôle de la vue."),
        ("2025-11-16 10:30:00", 7, 48, "Confirmé", "Consultation neurologique."),
        ("2025-11-17 12:00:00", 8, 49, "En attente", "Douleur à la jambe."),
        ("2025-11-18 09:30:00", 9, 50, "Confirmé", "Suivi thyroïde."),
        ("2025-11-19 15:00:00", 10, 51, "Confirmé", "Consultation psychologique.")
    ]

    for date_heure, patient, medecin, statut, notes in rdvs:
        cursor.execute("""
            INSERT INTO rendezvous (date_heure, patient_id, medecin_id, statut, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (date_heure, patient, medecin, statut, notes))

    connection.commit()
    print("Rendez-vous insérés.")


# ================= Avis =================
def seed_avis(connection, cursor):
    
        avis = [
            (1, 42, 5, "Médecin très compétent et à l’écoute."),
            (2, 43, 4, "Bon accueil et explications claires."),
            (3, 44, 5, "Très bon suivi pour les enfants."),
            (4, 45, 4, "Service professionnel."),
            (5, 46, 3, "Délai d’attente un peu long."),
            (6, 47, 5, "Excellent ophtalmologue."),
            (7, 48, 4, "Expérience positive."),
            (8, 49, 5, "Traitement efficace."),
            (9, 50, 4, "Très bon suivi médical."),
            (10, 51, 5, "Très compréhensive et à l’écoute.")
        ]


        for patient, medecin, note, commentaire in avis:
            cursor.execute("""
                INSERT INTO avis (patient_id, medecin_id, note, commentaire)
                VALUES (%s, %s, %s, %s)
            """, (patient, medecin, note, commentaire))

        connection.commit()
        print("Avis insérés.")


# ================= Statistiques =================
def seed_statistiques(connection, cursor):
    stats = [
    (42, 120, 85, 40, 4.7),
    (43, 95, 70, 35, 4.4),
    (44, 80, 65, 25, 4.8),
    (45, 60, 50, 20, 4.1),
    (46, 130, 100, 50, 4.6),
    (47, 75, 60, 22, 4.5),
    (48, 55, 48, 15, 4.3),
    (49, 90, 70, 30, 4.6),
    (50, 85, 75, 32, 4.5),
    (51, 100, 80, 40, 4.9)
]


    for medecin, total_rdv, total_patients, total_avis, moyenne in stats:
        cursor.execute("""
            INSERT INTO statistiques (medecin_id, total_rdv, total_patients, total_avis, moyenne_notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (medecin, total_rdv, total_patients, total_avis, moyenne))

    connection.commit()
    print("Statistiques insérées.")

# Spécialités marocaines
def seed_specialisations(cursor):
    specialites = [
        ("Cardiologie", "Traitement des maladies du cœur"),
        ("Dermatologie", "Soins de la peau et des ongles"),
        ("Pédiatrie", "Santé des enfants"),
        ("Neurologie", "Étude et traitement des maladies du système nerveux"),
        ("Orthopédie", "Appareil locomoteur et os"),
        ("Gynécologie", "Santé des femmes")
    ]
    for nom, description in specialites:
        cursor.execute("""
            INSERT INTO specialisations (nom, description)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE description = VALUES(description)
        """, (nom, description))
    print("Spécialités insérées.")
def seed_all(cursor):
    seed_patients(cursor)
    seed_medecins(cursor)
    seed_disponibilites(cursor)
    seed_rendezvous(cursor)
    seed_avis(cursor)
    seed_statistiques(cursor)
    seed_specialisations(cursor)  # <- Ajout ici
    print("Données marocaines insérées avec succès.")
