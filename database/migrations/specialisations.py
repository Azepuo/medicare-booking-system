def up(connection):
    """Créer la table specialisations et ajouter la colonne id_specialisation à la table medecins"""
    cursor = connection.cursor()
    

    try:
        # Créer la table specialisations si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS specialisations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL UNIQUE,
                description TEXT
            )
        """)
        
        # Vérifier si la colonne 'id_specialisation' existe déjà dans la table 'medecins'
        cursor.execute("""
            SHOW COLUMNS FROM medecins LIKE 'id_specialisation'
        """)
        result = cursor.fetchone()

        # Ajouter la colonne 'id_specialisation' si elle n'existe pas
        if not result:
            cursor.execute("""
                ALTER TABLE medecins
                ADD COLUMN id_specialisation INT;
            """)
        
        # Ajouter la contrainte de clé étrangère pour la colonne id_specialisation si elle n'existe pas déjà
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_NAME = 'medecins' 
            AND COLUMN_NAME = 'id_specialisation'
        """)
        constraint = cursor.fetchone()

        if not constraint:
            cursor.execute("""
                ALTER TABLE medecins
                ADD CONSTRAINT fk_specialisation
                FOREIGN KEY (id_specialisation)
                REFERENCES specialisations(id)
                ON DELETE SET NULL;
            """)

        # Ajouter les spécialités manquantes dans la table specialisations
        ajouter_specialites_manquantes(connection)  # Passer la connexion ici

        # Mettre à jour la colonne id_specialisation dans medecins en fonction de la spécialité
        cursor.execute("""
            UPDATE medecins AS m
            JOIN specialisations AS s ON m.specialite = s.nom
            SET m.id_specialisation = s.id;
        """)

        connection.commit()
        print("✅ Table 'specialisations' créée et 'id_specialisation' ajoutée à 'medecins' avec succès")
    
    except Exception as e:
        connection.rollback()
        print(f"❌ Une erreur s'est produite : {e}")


def down(connection):
    """Supprimer la table specialisations et la colonne id_specialisation de medecins"""
    cursor = connection.cursor()

    try:
        # Supprimer la contrainte de clé étrangère
        cursor.execute("""
            ALTER TABLE medecins
            DROP FOREIGN KEY fk_specialisation;
        """)

        # Supprimer la colonne id_specialisation de la table medecins
        cursor.execute("""
            ALTER TABLE medecins
            DROP COLUMN id_specialisation;
        """)

        # Supprimer la colonne 'description' dans la table 'specialisations'
        cursor.execute("""
            ALTER TABLE specialisations
            DROP COLUMN description;
        """)

        # Supprimer la table specialisations
        cursor.execute("DROP TABLE IF EXISTS specialisations")

        connection.commit()
        print("✅ Table 'specialisations' supprimée et 'id_specialisation' retirée de 'medecins' avec succès")
    
    except Exception as e:
        connection.rollback()
        print(f"❌ Une erreur s'est produite lors du rollback : {e}")


def ajouter_specialites_manquantes(connection):
    """Ajouter les spécialités manquantes dans la table specialisations"""
    cursor = connection.cursor()

    try:
        # Spécialités dans la table medecins qui ne sont pas dans specialisations
        cursor.execute("""
            SELECT DISTINCT specialite FROM medecins
            WHERE specialite NOT IN (SELECT nom FROM specialisations)
        """)
        specialites_manquantes = cursor.fetchall()

        for specialite in specialites_manquantes:
            # Ajouter chaque spécialité manquante dans la table specialisations
            cursor.execute("""
                INSERT INTO specialisations (nom)
                VALUES (%s)
            """, (specialite[0],))

        connection.commit()
        print("✅ Spécialités manquantes ajoutées dans la table 'specialisations'.")
    
    except Exception as e:
        connection.rollback()
        print(f"❌ Une erreur s'est produite lors de l'ajout des spécialités manquantes : {e}")
