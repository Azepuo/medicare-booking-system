from flask import Flask
from app.routes.medecin_routes import medecin

def create_app():
    app = Flask(__name__)
    app.secret_key = "SECRET_KEY"

    # Register blueprint
    app.register_blueprint(medecin, url_prefix='/medecin')

    @app.route('/')
    def index():
        return "<h1>Accueil OK</h1>"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
