# database/migrations/create_tables.py

def down(cursor):
    tables = [
        "statistiques", 
        "avis", 
        "rendezvous", 
        "disponibilites", 
        "notifications", # Ajouté
        "admins", # Ajouté
        "medecins", 
        "patients"
    ]
    # L'ordre n'est pas critique ici car nous utilisons DROP TABLE IF EXISTS
    for table in tables:
        # Utiliser un backtick (`) pour les noms de table est une bonne pratique, mais pas obligatoire ici.
        cursor.execute(f"DROP TABLE IF EXISTS `{table}`") 
    print(" Anciennes tables supprimées.")

def up(cursor):
    # 1. TABLE PATIENTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL, -- AJOUTÉ : Essentiel pour l'authentification
            telephone VARCHAR(20),
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. TABLE MEDECINS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medecins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL,
            specialite VARCHAR(100),
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL, -- AJOUTÉ : Essentiel pour l'authentification
            description TEXT,
            annees_experience INT,
            tarif_consultation DECIMAL(10, 2) -- CHANGÉ : Utiliser DECIMAL pour la monnaie (plus précis que FLOAT)
        )
    """)
    
    # 3. TABLE ADMINS -- AJOUTÉE : Nécessaire pour le modèle Admin
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL, -- Essentiel pour l'authentification
            date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. TABLE NOTIFICATIONS -- AJOUTÉE : Nécessaire pour le modèle Notification
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL, -- Peut être patient_id ou medecin_id ou admin_id
            user_role VARCHAR(20) NOT NULL, -- 'patient', 'medecin', 'admin'
            message TEXT NOT NULL,
            lue BOOLEAN DEFAULT FALSE,
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 5. TABLE DISPONIBILITES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disponibilites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            medecin_id INT,
            jour_semaine VARCHAR(20) NOT NULL, -- Ajout de NOT NULL
            heure_debut TIME NOT NULL,
            heure_fin TIME NOT NULL,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    # 6. TABLE RENDEZVOUS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rendezvous (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date_heure DATETIME NOT NULL, -- Ajout de NOT NULL
            patient_id INT,
            medecin_id INT,
            statut VARCHAR(50) NOT NULL, -- Ajout de NOT NULL (e.g., 'Confirmé', 'Annulé', 'En attente')
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    # 7. TABLE AVIS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT,
            medecin_id INT,
            note INT CHECK (note >= 1 AND note <= 5) NOT NULL, -- AJOUTÉ : Contrainte pour une note entre 1 et 5
            commentaire TEXT,
            date_avis DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    # 8. TABLE STATISTIQUES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistiques (
            id INT AUTO_INCREMENT PRIMARY KEY,
            medecin_id INT UNIQUE, -- CHANGÉ : Un médecin n'a besoin que d'une seule ligne de statistiques
            total_rdv INT DEFAULT 0 NOT NULL,
            total_patients INT DEFAULT 0 NOT NULL,
            total_avis INT DEFAULT 0 NOT NULL,
            moyenne_notes DECIMAL(3, 2) DEFAULT 0.00 NOT NULL, -- CHANGÉ : Utiliser DECIMAL pour la moyenne
            FOREIGN KEY (medecin_id) REFERENCES medecins(id) ON DELETE CASCADE
        )
    """)

    print(" Tables créées avec succès.")
    