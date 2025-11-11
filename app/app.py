from flask import Flask,send_from_directory




app = Flask(__name__)

# --- Enregistrement des Blueprints ---


# --- Route d'accueil globale ---


# --- Fichiers statiques ---
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# --- Lancement du serveur ---
if __name__ == '__main__':
 
    print("🏠 Accueil: http://localhost:5000/\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
