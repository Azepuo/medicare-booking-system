import xmlrpc.client

# Connexion au serveur RPC
server = xmlrpc.client.ServerProxy("http://localhost:9000")

# Tester la méthode get_patient_info avec un patient_id
patient_id = 1  # Remplace par un ID de patient valide dans ta base de données
patient_info = server.get_patient_info(patient_id)
print("Patient Info:", patient_info)

# Tester la méthode get_dashboard pour afficher le tableau de bord
dashboard = server.get_dashboard(patient_id)
print("Dashboard:", dashboard)

# Tester la méthode get_all_appointments pour récupérer tous les rendez-vous du patient
appointments = server.get_all_appointments(patient_id)
print("All Appointments:", appointments)

# Tester la méthode get_profile pour afficher le profil du patient
profile = server.get_profile(patient_id)
print("Patient Profile:", profile)

# Tester la méthode get_doctors pour récupérer les médecins par spécialité
doctors = server.get_doctors("cardiologie")  # Remplace par une spécialité existante
print("Doctors in cardiology:", doctors)
# Exemple de mise à jour d'un rendez-vous
appointment_id = 1
medecin_id = 2
date = '2025-12-05'
time_str = '14:00'
notes = 'Changement d\'heuree'
patient_id = 123

response = server.update_appointment(appointment_id, medecin_id, date, time_str, notes, patient_id)
print("Updated Appointment:", response)
