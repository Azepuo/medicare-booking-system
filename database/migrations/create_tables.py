import mysql.connector

def down(cursor):
    tables = [
        "facture_services",
        "factures",
        "services",
        "statistiques",
        "avis",
        "rendezvous",
        "disponibilites_medecin",
        "medecins",
        "patients",
        "admin"
    ]

    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    print("✅ Toutes les tables ont été supprimées.")


def up(cursor):
    # ---------- Patients ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(150) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            telephone VARCHAR(20),
            cin VARCHAR(20) UNIQUE,
            date_naissance DATE,
            sexe ENUM('Homme', 'Femme') NOT NULL,
            date_inscription DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------- Médecins ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medecins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(150) NOT NULL,
            specialite VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            telephone VARCHAR(20),
            annees_experience INT,
            tarif_consultation DECIMAL(10,2),
            description TEXT,
            statut ENUM('Actif', 'En congé', 'Inactif') DEFAULT 'Actif',
            date_inscription DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------- Disponibilités Médecins ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disponibilites_medecin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            medecin_id INT NOT NULL,
            date_disponible DATE NOT NULL,
            heure_debut TIME,
            heure_fin TIME,
            disponible TINYINT(1) DEFAULT 1,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    # ---------- Rendez-vous ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rendezvous (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT,
            medecin_id INT,
            date_rdv DATE NOT NULL,
            heure_rdv TIME NOT NULL,
            statut ENUM('en_attente', 'terminé', 'annulé') DEFAULT 'en_attente',
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    # ---------- Avis ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT,
            medecin_id INT,
            note INT,
            commentaire TEXT,
            date_avis DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    # ---------- Statistiques ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistiques (
            id INT AUTO_INCREMENT PRIMARY KEY,
            medecin_id INT,
            total_rdv INT DEFAULT 0,
            total_patients INT DEFAULT 0,
            total_avis INT DEFAULT 0,
            moyenne_notes FLOAT DEFAULT 0,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    # ---------- Services ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom_service VARCHAR(100) NOT NULL,
            prix_unitaire DECIMAL(10,2) NOT NULL,
            description TEXT
        )
    """)

    # ---------- Factures ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS factures (
            id INT AUTO_INCREMENT PRIMARY KEY,
            rdv_id INT NOT NULL,
            date_facture DATE NOT NULL,
            montant_total DECIMAL(10,2) DEFAULT 0,
            statut VARCHAR(20) DEFAULT 'non_payé',
            FOREIGN KEY (rdv_id) REFERENCES rendezvous(id)
        )
    """)

    # ---------- Facture Services ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facture_services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            facture_id INT NOT NULL,
            service_id INT NOT NULL,
            quantite INT NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (facture_id) REFERENCES factures(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    """)

    # ---------- Admin ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom_complet VARCHAR(150) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            telephone VARCHAR(30),
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME DEFAULT NULL,
            photo VARCHAR(255) DEFAULT NULL
        )
    """)

    # ---------- Seed Services ----------
    cursor.execute("""
        INSERT INTO services (nom_service, prix_unitaire, description) VALUES
        ('Consultation', 350.00, 'Consultation médicale générale'),
        ('Examens de laboratoire', 450.00, 'Analyses et tests en laboratoire'),
        ('Radiologie', 600.00, 'Imagerie médicale par rayons X'),
        ('Échographie', 500.00, 'Imagerie par ultrasons'),
        ('Injection', 120.00, 'Injection médicamenteuse'),
        ('Pansement', 80.00, 'Soin et pansement'),
        ('Scanner', 1200.00, 'Scanner médical'),
        ('IRM', 1500.00, 'Imagerie par résonance magnétique')
    """)

    print("✅ Base de données créée avec succès !")


# ---------- Execution ----------
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
