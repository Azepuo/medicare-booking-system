# app/routes/authentification/authentification_routes.py
from flask import Blueprint, request, redirect, make_response, jsonify, render_template
import jwt, datetime
from models.User import User

auth_bp = Blueprint("auth", __name__)

SECRET_KEY = "secret123"
REFRESH_SECRET_KEY = "refresh123"

# ---------------- ACCUEIL ----------------
@auth_bp.route("/")
def accueil():
    token = request.cookies.get("access_token")
    is_authenticated = False

    if token:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            is_authenticated = True
        except:
            pass

    return render_template(
        "acceuil/index.html",
        is_authenticated=is_authenticated
    )
# ---------------- LOGIN ----------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("login_email", "").strip().lower()
    password = request.form.get("login_password", "")

    user = User.get_by_email(email)

    if not user or not user.check_password(password):
        return render_template(
            "auth/login.html",
            error="Email ou mot de passe incorrect"
        )

    access_token = jwt.encode({
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }, SECRET_KEY, algorithm="HS256")

    refresh_token = jwt.encode({
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, REFRESH_SECRET_KEY, algorithm="HS256")

    url_map = {
        "PATIENT": "http://localhost:5001/dashboard",
        "MEDECIN": "http://localhost:5002/dashboard",
        "ADMIN": "http://127.0.0.1:5003/admin/dashboard"
    }

    response = make_response(redirect(url_map.get(user.role, "/")))
    response.set_cookie("access_token", access_token, httponly=True, samesite="Lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Lax")
    return response


# ---------------- REGISTER ----------------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    # Récupérer tous les champs du formulaire
    nom = request.form.get("register_fullname")  
    email = request.form.get("register_email")
    telephone = request.form.get("register_tele")
    password = request.form.get("password")
    confirm_password = request.form.get("register_confirm_password")

    if not all([nom, email, password, confirm_password]):
        return "Tous les champs sont requis", 400

    if password != confirm_password:
        return "Les mots de passe ne correspondent pas", 400

    if User.get_by_email(email):
        return "Cet email est déjà utilisé", 400

    # Créer l'utilisateur PATIENT
    new_user = User(
        nom=nom,
        email=email,
        role="PATIENT",
        telephone=telephone
    )
    new_user.set_password(password)
    new_user.save()

    return redirect("/login")


# ---------------- REFRESH ----------------
@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return "Refresh token manquant", 401

    try:
        data = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return "Refresh token expiré", 401
    except:
        return "Token invalide", 401

    new_access_token = jwt.encode({
        "user_id": data["user_id"],
        "role": data["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }, SECRET_KEY, algorithm="HS256")

    response = jsonify({"message": "Access token rafraîchi"})
    response.set_cookie("access_token", new_access_token, httponly=True, samesite="Lax")
    return response

# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
def logout():
    response = redirect("/")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response




