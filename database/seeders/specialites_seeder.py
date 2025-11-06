def run(connection):
    """Seeder des spécialités médicales"""
    cursor = connection.cursor()
    
    specialites = [
        ('Cardiologie', 'Spécialiste du cœur et des vaisseaux sanguins'),
        ('Pédiatrie', 'Médecine des enfants'),
        ('Dermatologie', 'Spécialiste de la peau'),
        ('Gynécologie', 'Santé féminine'),
        ('Neurologie', 'Spécialiste du système nerveux'),
        ('Ophtalmologie', 'Spécialiste des yeux'),
        ('Orthopédie', 'Spécialiste des os et articulations'),
        ('Psychiatrie', 'Santé mentale'),
        ('Radiologie', 'Imagerie médicale'),
        ('Chirurgie', 'Interventions chirurgicales')
    ]
    
    cursor.executemany("""
        INSERT IGNORE INTO specialites (nom, description) 
        VALUES (%s, %s)
    """, specialites)
    
    connection.commit()
    print(f"✅ {len(specialites)} spécialités insérées")