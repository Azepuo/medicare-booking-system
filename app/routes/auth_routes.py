# app/routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
# Importez votre instance de connexion à la BDD
# from database.connection import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Requête pour récupérer l'utilisateur
        query = "SELECT id, nom, email, password, role FROM patient WHERE email = %s"
        user = db.fetch_one(query, (email,))
        
        if user and check_password_hash(user['password'], password):
            # Connexion réussie
            session['user_id'] = user['id']
            session['user_role'] = user.get('role', 'patient')
            session['user_name'] = user['nom']
            flash(f"Connexion réussie ! Bienvenue, {user['nom']}.", 'success')
            
            if session['user_role'] == 'patient':
                return redirect(url_for('patient.accueil'))
            # elif session['user_role'] == 'medecin':
            #     return redirect(url_for('medecin.accueil'))
            # elif session['user_role'] == 'admin':
            #     return redirect(url_for('admin.dashboard'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form.get('nom')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('auth/register.html')

        hashed_password = generate_password_hash(password)

        insert_query = """
        INSERT INTO patient (nom, email, password, role) 
        VALUES (%s, %s, %s, 'patient')
        """
        success = db.execute_query(insert_query, (nom, email, hashed_password))

        if success:
            flash('Inscription réussie ! Veuillez vous connecter.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash("Erreur lors de l'inscription. L'email existe peut-être déjà.", 'error')
            
    return render_template('auth/register.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('user_name', None)
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))
