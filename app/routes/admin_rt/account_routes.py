from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import xmlrpc.client
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint("admin_bp", __name__)

# ✅ Client RPC
rpc = xmlrpc.client.ServerProxy("http://localhost:8002", allow_none=True)


# ✅ 1) AFFICHAGE DU COMPTE ADMIN
@admin_bp.route("/account", methods=["GET"])
def admin_account():
    admin = rpc.get_admin()

    if not admin:
        flash("⚠ Impossible de charger les informations administrateur.", "error")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/account.html", admin=admin)


# ✅ 2) MISE À JOUR DES INFORMATIONS (AVEC PHOTO, SANS MOT DE PASSE)
@admin_bp.route("/account", methods=["POST"])
def update_admin_account():

    # 🔹 Gestion de la photo (optionnelle)
    photo_file = request.files.get("photo")
    photo_filename = None

    if photo_file and photo_file.filename:
        filename = secure_filename(photo_file.filename)

        # chemin : <racine_app>/static/uploads/filename
        upload_folder = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        photo_path = os.path.join(upload_folder, filename)
        photo_file.save(photo_path)

        # Ce qui sera stocké en BDD (pour url_for('static', filename=...))
        photo_filename = filename

    data = {
        "nom_complet": request.form.get("nom_complet"),
        "email": request.form.get("email"),
        "telephone": request.form.get("telephone"),
        "username": request.form.get("username"),
        "photo": photo_filename  # peut être None si pas de nouvelle photo
    }

    result = rpc.update_admin(data)

    if result.get("error"):
        flash(f"⚠ {result['error']}", "error")
    else:
        flash("✅ Informations mises à jour avec succès", "success")

    return redirect(url_for("admin_bp.admin_account"))


# ✅ 3) CHANGEMENT DE MOT DE PASSE
@admin_bp.route("/account/password", methods=["POST"])
def update_admin_password():

    current_pwd = request.form.get("current_pwd")
    new_pwd = request.form.get("new_pwd")
    confirm_pwd = request.form.get("confirm_password")

    # ✅ Vérifier tous les champs
    if not current_pwd or not new_pwd or not confirm_pwd:
        flash("⚠ Merci de remplir tous les champs.", "error")
        return redirect(url_for("admin_bp.admin_account"))

    # ✅ Vérifier confirmation
    if new_pwd != confirm_pwd:
        flash("⚠ Les mots de passe ne correspondent pas.", "error")
        return redirect(url_for("admin_bp.admin_account"))

    # ✅ Appel RPC
    result = rpc.update_admin_password(current_pwd, new_pwd)

    if result.get("error"):
        flash(f"⚠ {result['error']}", "error")
    else:
        flash("✅ Mot de passe mis à jour avec succès.", "success")

    return redirect(url_for("admin_bp.admin_account"))
