import bcrypt

DEFAULT_PASSWORD = "Pass1234"

# =========================
# UTILS
# =========================
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# =========================
# SEED ALL
# =========================
def seed_all(cursor):
    seed_admins(cursor)
    seed_patients(cursor)
    seed_medecins(cursor)
    seed_disponibilites(cursor)
    seed_rendezvous(cursor)
    seed_avis(cursor)
    seed_statistiques(cursor)
    print("✅ Données marocaines insérées avec succès.")


# =========================
# ADMINS
# =========================
def seed_admins(cursor):
    pwd = hash_password(DEFAULT_PASSWORD)
    cursor.execute("""
        INSERT INTO admins (nom, email, username, password, telephone)
        VALUES (%s, %s, %s, %s, %s)
    """, ("Super Admin", "admin@clinique.ma", "admin", pwd, "0537000000"))
    print("Admin inséré.")


# =========================
# PATIENTS
# =========================
def seed_patients(cursor):
    pwd = hash_password(DEFAULT_PASSWORD)
    patients = [
        ("Yassine El Amrani", "yassine@gmail.com", "0612345678"),
        ("Khadija Benali", "khadija@gmail.com", "0678123456"),
        ("Omar Essafi", "omar@gmail.com", "0655332211"),
        ("Fatima Zahra", "fatima@gmail.com", "0666778899"),
    ]
    for nom, email, tel in patients:
        cursor.execute("""
            INSERT INTO patients (nom, email, password, telephone)
            VALUES (%s, %s, %s, %s)
        """, (nom, email, pwd, tel))
    print("Patients insérés.")


# =========================
# MEDECINS
# =========================
def seed_medecins(cursor):
    pwd = hash_password(DEFAULT_PASSWORD)
    medecins = [
        ("Dr Rachid", "Cardiologie", "rachid@clinique.ma", 300),
        ("Dr Salma", "Dermatologie", "salma@clinique.ma", 250),
        ("Dr Youssef", "Pédiatrie", "youssef@hopital.ma", 220),
    ]
    for nom, spec, email, tarif in medecins:
        cursor.execute("""
            INSERT INTO medecins (nom, specialite, email, password, tarif_consultation)
            VALUES (%s, %s, %s, %s, %s)
        """, (nom, spec, email, pwd, tarif))
    print("Médecins insérés.")


# =========================
# DISPONIBILITES
# =========================
def seed_disponibilites(cursor):
    dispos = [
        (1, "Lundi", "09:00", "12:00"),
        (1, "Jeudi", "14:00", "17:00"),
        (2, "Mardi", "10:00", "13:00"),
        (3, "Mercredi", "09:00", "12:00"),
    ]
    for m, jour, d, f in dispos:
        cursor.execute("""
            INSERT INTO disponibilites (medecin_id, jour_semaine, heure_debut, heure_fin)
            VALUES (%s, %s, %s, %s)
        """, (m, jour, d, f))
    print("Disponibilités insérées.")


# =========================
# RENDEZ-VOUS
# =========================
def seed_rendezvous(cursor):
    rdvs = [
        (1, 1, "2025-11-10", "10:00", "confirmé"),
        (2, 2, "2025-11-11", "11:30", "en_attente"),
        (3, 3, "2025-11-12", "09:00", "annulé"),
    ]
    for p, m, d, h, s in rdvs:
        cursor.execute("""
            INSERT INTO rendezvous (patient_id, medecin_id, date_rdv, heure_rdv, statut)
            VALUES (%s, %s, %s, %s, %s)
        """, (p, m, d, h, s))
    print("Rendez-vous insérés.")


# =========================
# AVIS
# =========================
def seed_avis(cursor):
    avis = [
        (1, 1, 5, "Excellent médecin"),
        (2, 2, 4, "Bon accueil"),
        (3, 3, 5, "Très professionnel"),
    ]
    for p, m, n, c in avis:
        cursor.execute("""
            INSERT INTO avis (patient_id, medecin_id, note, commentaire)
            VALUES (%s, %s, %s, %s)
        """, (p, m, n, c))
    print("Avis insérés.")


# =========================
# STATISTIQUES
# =========================
def seed_statistiques(cursor):
    stats = [
        (1, 10, 8, 3, 4.6),
        (2, 7, 6, 2, 4.4),
        (3, 12, 9, 4, 4.8),
    ]
    for m, r, p, a, moy in stats:
        cursor.execute("""
            INSERT INTO statistiques (medecin_id, total_rdv, total_patients, total_avis, moyenne_notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (m, r, p, a, moy))
    print("Statistiques insérées.")
