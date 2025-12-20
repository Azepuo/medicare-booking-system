#C:\Users\pc\medicare-db\app\routes\authentification\auth_decorators.py
from functools import wraps
from flask import request, jsonify
import jwt

SECRET_KEY = "secret123"

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.cookies.get("access_token")
            if not token:
                return jsonify({"success": False, "message": "Non authentifié"}), 401
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return jsonify({"success": False, "message": "Token expiré"}), 401
            except:
                return jsonify({"success": False, "message": "Token invalide"}), 401

            if data["role"] != required_role:
                return jsonify({"success": False, "message": "Accès interdit"}), 403

            request.user_id = data["user_id"]
            return f(*args, **kwargs)
        return wrapper
    return decorator
