def run(connection):
    """Seeder des médecins"""
    cursor = connection.cursor()
    
    medecins = [
        ('Dr. Sophie Laurent', 'Cardiologie', 'sophie.laurent@clinique.com', 15, 80.00, 'Cardiologue expérimentée avec expertise en hypertension'),
        ('Dr. Pierre Moreau', 'Pédiatrie', 'pierre.moreau@clinique.com', 10, 60.00, 'Pédiatre passionné par la santé des enfants'),
        ('Dr. Marie Petit', 'Dermatologie', 'marie.petit@clinique.com', 8, 70.00, 'Spécialiste en dermatologie esthétique et médicale'),
        ('Dr. Jean Dubois', 'Neurologie', 'jean.dubois@clinique.com', 20, 90.00, 'Neurologue renommé'),
        ('Dr. Alice Martin', 'Gynécologie', 'alice.martin@clinique.com', 12, 75.00, 'Gynécologue-obstétricienne'),
        ('Dr. Marc Bernard', 'Ophtalmologie', 'marc.bernard@clinique.com', 9, 65.00, 'Spécialiste de la vision'),
        ('Dr. Julie Robert', 'Psychiatrie', 'julie.robert@clinique.com', 11, 85.00, 'Psychiatre pour adultes et adolescents')
    ]
    
    cursor.executemany("""
        INSERT IGNORE INTO medecins (nom, specialite, email, annees_experience, tarif_consultation, description) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, medecins)
    
    connection.commit()
    print(f"✅ {len(medecins)} médecins insérés")