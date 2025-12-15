from flask import Flask
from app.routes.admin_routes import admin_bp

app = Flask(__name__)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5003)
