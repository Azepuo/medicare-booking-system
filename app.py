from app import create_app
from app.extensions import db

app = create_app()

# Crée les tables si elles n'existent pas
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    print("🚀 Serveur Flask démarré sur http://localhost:5000")
    app.run(debug=True)
