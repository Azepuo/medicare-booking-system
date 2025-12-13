#  Plateforme RDV Médicaux

Système de rendez-vous médicaux avec architecture distribuée Flask + RPC

##  Installation Rapide

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/medicare-booking-system.git
cd medicare-booking-system

# 2. Installer les dépendances
pip install -r requirements.txt

# 3 Tester la connexion
<<<<<<< HEAD
python -c "from database.connection_p import test_connection; test_connection()"
=======
python -c "from database.connection_m import test_connection; test_connection()"
>>>>>>> Mariam_Moumen
# 4 Lancer la création complète de la base (migrations + seeders)
python scripts/setup_database.py
# 5. Démarrer l'application
python app/app.py

