import mysql.connector

# =========================
# DROP TABLES
# =========================
def down(cursor):
    tables = [
        "facture_services",
        "factures",
        "services",
        "statistiques",
        "avis",
        "rendezvous",
        "disponibilites",
        "notifications",
        "admins",
        "medecins",
        "patients"
    ]

    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS `{table}`")

    print("✅ Toutes les tables ont été supprimées.")


# =========================
# CREATE TABLES
# =========================
def up(cursor):

    # ---------- PATIENTS ----------
    cursor.execute("""
        CREATE TABLE patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(150) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            telephone VARCHAR(20),
            cin VARCHAR(20) UNIQUE,
            sexe ENUM('Homme','Femme'),
            date_naissance DATE,
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------- MEDECINS ----------
    cursor.execute("""
        CREATE TABLE medecins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(150) NOT NULL,
            specialite VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            telephone VARCHAR(20),
            annees_experience INT,
            tarif_consultation DECIMAL(10,2),
            description TEXT,
            statut ENUM('Actif','En congé','Inactif') DEFAULT 'Actif',
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------- ADMINS ----------
    cursor.execute("""
        CREATE TABLE admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(150) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            telephone VARCHAR(30),
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME DEFAULT NULL,
            photo VARCHAR(255)
        )
    """)

    # ---------- NOTIFICATIONS ----------
    cursor.execute("""
        CREATE TABLE notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            user_role ENUM('patient','medecin','admin') NOT NULL,
            message TEXT NOT NULL,
            lue BOOLEAN DEFAULT FALSE,
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------- DISPONIBILITES ----------
    cursor.execute("""
        CREATE TABLE disponibilites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            medecin_id INT NOT NULL,
            jour_semaine VARCHAR(20) NOT NULL,
            heure_debut TIME NOT NULL,
            heure_fin TIME NOT NULL,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    # ---------- RENDEZ-VOUS ----------
    cursor.execute("""
        CREATE TABLE rendezvous (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT NOT NULL,
            medecin_id INT NOT NULL,
            date_rdv DATE NOT NULL,
            heure_rdv TIME NOT NULL,
            statut ENUM('en_attente','confirmé','annulé','terminé') DEFAULT 'en_attente',
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    # ---------- AVIS ----------
    cursor.execute("""
        CREATE TABLE avis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT NOT NULL,
            medecin_id INT NOT NULL,
            note INT CHECK(note BETWEEN 1 AND 5),
            commentaire TEXT,
            date_avis DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    # ---------- STATISTIQUES ----------
    cursor.execute("""
        CREATE TABLE statistiques (
            id INT AUTO_INCREMENT PRIMARY KEY,
            medecin_id INT UNIQUE,
            total_rdv INT DEFAULT 0,
            total_patients INT DEFAULT 0,
            total_avis INT DEFAULT 0,
            moyenne_notes DECIMAL(3,2) DEFAULT 0,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    # ---------- SERVICES ----------
    cursor.execute("""
        CREATE TABLE services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom_service VARCHAR(100) NOT NULL,
            prix_unitaire DECIMAL(10,2) NOT NULL,
            description TEXT
        )
    """)

    # ---------- FACTURES ----------
    cursor.execute("""
        CREATE TABLE factures (
            id INT AUTO_INCREMENT PRIMARY KEY,
            rdv_id INT NOT NULL,
            date_facture DATE NOT NULL,
            montant_total DECIMAL(10,2) DEFAULT 0,
            statut ENUM('payé','non_payé') DEFAULT 'non_payé',
            FOREIGN KEY (rdv_id) REFERENCES rendezvous(id) ON DELETE CASCADE
        )
    """)

    # ---------- FACTURE SERVICES ----------
    cursor.execute("""
        CREATE TABLE facture_services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            facture_id INT NOT NULL,
            service_id INT NOT NULL,
            quantite INT NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (facture_id) REFERENCES factures(id) ON DELETE CASCADE,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
        )
    """)

    # ---------- SEED SERVICES ----------
    cursor.execute("""
        INSERT INTO services (nom_service, prix_unitaire, description) VALUES
        ('Consultation',350,'Consultation générale'),
        ('Analyse laboratoire',450,'Analyses médicales'),
        ('Radiologie',600,'Imagerie X-Ray'),
        ('Échographie',500,'Ultrasons'),
        ('Injection',120,'Injection médicale'),
        ('Pansement',80,'Soin infirmier')
    """)

    print("✅ Base de données créée avec succès.")


# =========================
# EXECUTION
# =========================
if __name__ == "__main__":
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="nom_de_ta_base"
    )

    cursor = conn.cursor()
    down(cursor)
    up(cursor)

    conn.commit()
    cursor.close()
    conn.close()

    print("🎉 Migration terminée.")
