from datetime import datetime, timedelta

def run(connection):
    """Seeder des rendez-vous"""
    cursor = connection.cursor()
    
    # Générer des dates de rendez-vous (prochains jours)
    base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    rendezvous = [
        (1, 1, base_date + timedelta(days=1), 'confirmé', 'Consultation routine cardiaque'),
        (2, 2, base_date + timedelta(days=2), 'confirmé', 'Première visite pédiatrique'),
        (3, 3, base_date + timedelta(days=1, hours=2), 'confirmé', 'Examen de la peau'),
        (4, 4, base_date + timedelta(days=3), 'confirmé', 'Suivi neurologique'),
        (5, 5, base_date + timedelta(days=2, hours=3), 'confirmé', 'Consultation gynécologique'),
        (6, 6, base_date + timedelta(days=4), 'confirmé', 'Contrôle de la vision'),
        (7, 7, base_date + timedelta(days=5), 'confirmé', 'Suivi psychiatrique'),
        (1, 2, base_date + timedelta(days=6), 'confirmé', 'Consultation pédiatrique')
    ]
    
    cursor.executemany("""
        INSERT IGNORE INTO rendezvous (patient_id, medecin_id, date_heure, statut, notes) 
        VALUES (%s, %s, %s, %s, %s)
    """, rendezvous)
    
    connection.commit()
    print(f"✅ {len(rendezvous)} rendez-vous insérés")