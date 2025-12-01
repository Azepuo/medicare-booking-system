from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models import Patient, Medecin, Admin
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

# ------------------ Helper pour récupérer un utilisateur par email ------------------
def get_user_by_email(email):
    return Patient.query.filter_by(email=email).first() \
        or Medecin.query.filter_by(email=email).first() \
        or Admin.query.filter_by(email=email).first()

# ------------------ LOGIN ------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user._get_current_object(), Admin):
            return redirect(url_for('admin.dashboard'))
        elif isinstance(current_user._get_current_object(), Medecin):
            return redirect(url_for('medecin.dashboard'))
        else:
            return redirect(url_for('patient.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = get_user_by_email(email)

        if not user or not check_password_hash(user.password, password):
            flash('Email ou mot de passe incorrect', 'danger')
            return render_template('auth/login.html')

        if isinstance(user, Medecin) and not user.approved:
            flash("Votre compte médecin est en attente d'approbation.", 'warning')
            return render_template('auth/login.html')

        login_user(user)
        flash('Connexion réussie', 'success')

        if isinstance(user, Admin):
            return redirect(url_for('admin.dashboard'))
        elif isinstance(user, Medecin):
            return redirect(url_for('medecin.dashboard'))
        else:
            return redirect(url_for('patient.dashboard'))

    return render_template('auth/login.html')


# ------------------ REGISTER ------------------
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('patient.dashboard'))

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'patient')  # rôle sélectionné dans le formulaire

        if not nom or not email or not password or not confirm_password or not role:
            flash('Veuillez remplir tous les champs', 'warning')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas", 'warning')
            return render_template('auth/register.html')

        if get_user_by_email(email):
            flash('Cet e-mail est déjà utilisé', 'warning')
            return render_template('auth/register.html')

        # Création selon rôle
        if role == 'patient':
            user = Patient(nom=nom, email=email)
        elif role == 'medecin':
            user = Medecin(nom=nom, email=email, approved=False)
        else:
            flash('Rôle invalide', 'danger')
            return render_template('auth/register.html')

        # Hash du mot de passe
        user.password = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()

        flash(f'Compte {role} créé avec succès. Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ------------------ LOGOUT ------------------
@auth.route('/logout')
def logout():
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('auth.login'))
