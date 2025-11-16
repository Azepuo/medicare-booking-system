def up(connection):
    """Migration initiale - Création des tables"""
    cursor = connection.cursor()
    
    # Table patients
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(150) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            telephone VARCHAR(20),
            cin VARCHAR(20) UNIQUE,
            date_naissance DATE,
            sexe ENUM('Homme', 'Femme') NOT NULL,
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table medecins
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
            statut ENUM('Actif', 'En congé', 'Inactif') DEFAULT 'Actif'
        )
    """)
    
    # Table rendezvous
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rendezvous (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT,
            medecin_id INT,
            date_heure DATETIME NOT NULL,
            statut ENUM('confirmé', 'annulé', 'terminé') DEFAULT 'confirmé',
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)
    
    # Table des spécialités (pour référence)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS specialites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL UNIQUE,
            description TEXT
        )
    """)
    
    connection.commit()
    print("✅ Tables créées avec succès")


def down(connection):
    """Rollback - Supprimer les tables"""
    cursor = connection.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS rendezvous")
    cursor.execute("DROP TABLE IF EXISTS patients")
    cursor.execute("DROP TABLE IF EXISTS medecins")
    cursor.execute("DROP TABLE IF EXISTS specialites")
    # Si vous avez une table 'migrations' dans votre système, gardez cette ligne,
    # sinon vous pouvez la commenter ou la retirer.
    # cursor.execute("DROP TABLE IF EXISTS migrations")
    
    connection.commit()
    print("✅ Tables supprimées avec succès")
