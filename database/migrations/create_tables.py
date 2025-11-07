# database/migrations/create_tables.py

def down(cursor):
    tables = ["statistiques", "avis", "rendezvous", "disponibilites", "medecins", "patients"]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    print(" Anciennes tables supprimées.")

def up(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            telephone VARCHAR(20),
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medecins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL,
            specialite VARCHAR(100),
            email VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            annees_experience INT,
            tarif_consultation FLOAT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disponibilites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            medecin_id INT,
            jour_semaine VARCHAR(20),
            heure_debut TIME,
            heure_fin TIME,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rendezvous (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date_heure DATETIME,
            patient_id INT,
            medecin_id INT,
            statut VARCHAR(50),
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

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

    print(" Tables créées avec succès.")
