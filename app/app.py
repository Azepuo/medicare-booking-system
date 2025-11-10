from flask import Flask, render_template, send_from_directory
from routes.admin_routes import admin
from routes.medecin_routes import medecin

app = Flask(__name__)

# --- Enregistrement des Blueprints ---
app.register_blueprint(admin)
app.register_blueprint(medecin)

# --- Route d'accueil globale ---


# --- Fichiers statiques ---
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# --- Lancement du serveur ---
if __name__ == '__main__':
    print("\n🚀 Serveur Flask démarré sur http://localhost:5000")
    print("🧩 Admin Dashboard: http://localhost:5000/admin/dashboard")
    print("⚕️ Médecin Dashboard: http://localhost:5000/medecin/dashboard")
    print("🏠 Accueil: http://localhost:5000/\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
