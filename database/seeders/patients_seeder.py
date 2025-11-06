def run(connection):
    """Seeder des patients"""
    cursor = connection.cursor()
    
    patients = [
        ('Alice Dupont', 'alice.dupont@email.com', '0123456789'),
        ('Bob Martin', 'bob.martin@email.com', '0234567890'),
        ('Claire Bernard', 'claire.bernard@email.com', '0345678901'),
        ('David Leroy', 'david.leroy@email.com', '0456789012'),
        ('Emma Petit', 'emma.petit@email.com', '0567890123'),
        ('François Moreau', 'francois.moreau@email.com', '0678901234'),
        ('Gabrielle Simon', 'gabrielle.simon@email.com', '0789012345'),
        ('Hugo Laurent', 'hugo.laurent@email.com', '0890123456')
    ]
    
    cursor.executemany("""
        INSERT IGNORE INTO patients (nom, email, telephone) 
        VALUES (%s, %s, %s)
    """, patients)
    
    connection.commit()
    print(f"✅ {len(patients)} patients insérés")