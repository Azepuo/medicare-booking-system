from flask import Flask
from app.routes.auth_routes import auth
from app.routes.main_routes import main

app = Flask(__name__)
app.secret_key = "votre_cle_secrete"

app.register_blueprint(auth)
app.register_blueprint(main)
