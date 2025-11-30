import mysql.connector

# Fonction pour supprimer toutes les tables (rollback)
def down(cursor):
    tables = ["statistiques", "avis", "rendezvous", "disponibilites", "admins", "medecins", "patients"]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    print("Toutes les tables supprimées avec succès.")

# Fonction pour créer toutes les tables
def up(cursor):

    # Table patients
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            telephone VARCHAR(20),
            password VARCHAR(255) NOT NULL,
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table medecins
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medecins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL,
            specialite VARCHAR(100),
            email VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            annees_experience INT,
            tarif_consultation FLOAT,
            password VARCHAR(255) NOT NULL
        )
    """)

    # Table admins
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table disponibilites
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

    # Table rendezvous
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

    # Table avis
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

    # Table statistiques
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

    print("Toutes les tables ont été créées avec succès.")

# Fonction de connexion à la base
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="",
        database="medicare_booking"
    )



# Fonction principale de migration
def run_migration(create=True)  :

    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        if create:
            up(cursor)
        else:
            down(cursor)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erreur: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # True pour créer, False pour supprimer
    run_migration(create=True)
