# Fichier : app/app.py (Le fichier principal)

from flask import Flask

# Importez les Blueprints que vous avez créés
from app.routes.auth_routes import auth
from app.routes.patient_routes import patient
# Assurez-vous d'avoir aussi 'medecin' et 'admin' ici quand ils seront prêts

app = Flask(__name__)

# Configuration de l'application
# SECRET_KEY est OBLIGATOIRE pour les sessions et flash
app.config['SECRET_KEY'] = 'une_cle_secrete_tres_sure_et_longue' 
# Ajoutez ici d'autres configurations (BDD, etc.)

# Enregistrement des Blueprints
app.register_blueprint(auth)
# Toutes les routes patient, y compris la racine '/', doivent être dans le Blueprint 'patient'
app.register_blueprint(patient) 


if __name__ == '__main__':
    print("🚀 Serveur Flask démarré sur http://localhost:5000")
    # Si 'app.py' est dans le dossier 'app/', le serveur doit être lancé via 'python app/app.py'
    app.run(debug=True)