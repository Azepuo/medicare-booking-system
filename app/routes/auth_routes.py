from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'medecin':
            return redirect(url_for('medecin.dashboard'))
        else:
            return redirect(url_for('patient.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Email ou mot de passe incorrect', 'danger')
            return render_template('auth/login.html')

        if user.role == 'medecin' and not user.approved:
            flash("Votre compte médecin est en attente d'approbation par l'administrateur.", 'warning')
            return render_template('auth/login.html')

        login_user(user)
        flash('Connexion réussie', 'success')

        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'medecin':
            return redirect(url_for('medecin.dashboard'))
        else:
            return redirect(url_for('patient.dashboard'))

    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('patient.dashboard'))

    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not fullname or not email or not password or not confirm_password:
            flash('Veuillez remplir tous les champs', 'warning')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas", "warning")
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Cet e-mail est déjà utilisé', 'warning')
            return render_template('auth/register.html')

        user = User(fullname=fullname, email=email, role='patient', approved=True)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Compte patient créé avec succès. Connectez-vous.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth.route('/logout')
def logout():
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('auth.login'))
