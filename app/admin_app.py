from flask import Flask
from app.routes.admin_routes import admin_bp
from app.rpc.auth_rpc.auth_rpc import auth_rpc

app = Flask(__name__)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_rpc)

if __name__ == "__main__":
    app.run(port=5003, debug=True)
