from flask import Flask
from app.routes import register_blueprints
from app.routes.api_routes import init_api_routes


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.secret_key = "votre_cle_secrete"

    # Register blueprints (auth, main, admin, medecin, patient)
    register_blueprints(app)

    # Register API routes (non-blueprint simple functions)
    init_api_routes(app)

    @app.route("/")
    def root():
        # Redirect root to main index or patient accueil as needed
        from flask import redirect, url_for
        return redirect(url_for("main.index"))

    return app


if __name__ == "__main__":
    app = create_app()
    print("App running: http://localhost:5000/")
    app.run(debug=True, host="0.0.0.0", port=5000)