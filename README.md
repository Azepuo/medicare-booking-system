#  Plateforme RDV Médicaux

Système de rendez-vous médicaux avec architecture distribuée Flask + RPC

##  Installation Rapide

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/medicare-booking-system.git
cd medicare-booking-system

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Initialiser la base de données
python scripts/setup_database.py

# 4. Démarrer l'application
python app/app.py


# Tester la connexion
python -c "from database.connection import test_connection; test_connection()"