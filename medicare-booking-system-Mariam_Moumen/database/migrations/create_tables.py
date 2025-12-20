# database/migrations/create_tables.py

def down(cursor):
    tables = [
        "notifications",
        "taches",
        "statistiques",
        "factures",
        "services",
        "avis",
        "rendezvous",
        "disponibilites",
        "medecins",
        "patients",
        "specialisations",
        "admin",
        "users"
    ]
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    print("✅ Anciennes tables supprimées.")


def up(cursor):
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

    # -------------------- USERS --------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(150) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role ENUM('ADMIN','MEDECIN','PATIENT') NOT NULL,
            telephone VARCHAR(20),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------- ADMIN --------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            nom_complet VARCHAR(150),
            telephone VARCHAR(30),
            username VARCHAR(50),
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_admin_user
                FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # -------------------- SPECIALISATIONS --------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS specialisations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL UNIQUE,
            description TEXT
        )
    """)

    # -------------------- MEDECINS --------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medecins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE,
            nom VARCHAR(150),
            email VARCHAR(100) UNIQUE,
            telephone VARCHAR(20),
            id_specialisation INT,
            tarif_consultation DECIMAL(10,2),
            statut ENUM('Actif','En congé','Inactif') DEFAULT 'Actif',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (id_specialisation) REFERENCES specialisations(id)
        )
    """)

    # -------------------- PATIENTS --------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE,
            nom VARCHAR(150),
            email VARCHAR(100) UNIQUE,
            telephone VARCHAR(20),
            sexe ENUM('Homme','Femme'),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """)

    # -------------------- RENDEZ-VOUS --------------------
    cursor.execute("""
         CREATE TABLE IF NOT EXISTS medecins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE,
            nom VARCHAR(150),
            email VARCHAR(100) UNIQUE,
            telephone VARCHAR(20),
            id_specialisation INT,
            tarif_consultation DECIMAL(10,2),
            statut ENUM('Actif','En congé','Inactif') DEFAULT 'Actif',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (id_specialisation) REFERENCES specialisations(id)
        )
    """)

    # -------------------- DISPONIBILITES --------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disponibilites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            jour_semaine VARCHAR(20) NOT NULL,
            heure_debut TIME NOT NULL,
            heure_fin TIME NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_jour (user_id, jour_semaine)
)
    """)

    # -------------------- AVIS --------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT,
            medecin_id INT,
            rendezvous_id INT,
            note INT,
            commentaire TEXT,
            date_avis DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE,
            FOREIGN KEY (rendezvous_id) REFERENCES rendezvous(id) ON DELETE SET NULL
        )
    """)

    # -------------------- SERVICES --------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom_service VARCHAR(100),
            prix_unitaire DECIMAL(10,2),
            description TEXT
        )
    """)

    # -------------------- FACTURES --------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS factures (
            id INT AUTO_INCREMENT PRIMARY KEY,
            rdv_id INT,
            montant_total DECIMAL(10,2),
            statut ENUM('payé','non_payé','annulé'),
            FOREIGN KEY (rdv_id) REFERENCES rendezvous(id) ON DELETE CASCADE
        )
    """)

    # -------------------- STATISTIQUES --------------------
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

    # -------------------- TACHES --------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS taches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titre VARCHAR(255),
            statut ENUM('complétée','non_complétée'),
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------- NOTIFICATIONS --------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT NOT NULL,
            titre VARCHAR(255),
            message TEXT,
            type ENUM(
                'rdv_confirme','rdv_annule','rdv_modifie',
                'rdv_termine','rappel_rdv','demande_avis'
            ),
            lue TINYINT(1) DEFAULT 0,
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_lecture DATETIME,
            rendezvous_id INT,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (rendezvous_id) REFERENCES rendezvous(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    print("✅ Toutes les tables créées avec succès.")
