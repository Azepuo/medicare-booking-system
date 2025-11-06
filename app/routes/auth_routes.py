# Fichier : app/routes/auth_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
# Importation de votre instance de connexion à la BDD
# from database.connection import db  #

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 1. Requête SQL pour trouver l'utilisateur par email et mot de passe (sans hachage)
        query = """
        SELECT id, nom, email, role 
        FROM patient 
        WHERE email = %s AND password = %s
        """
        # Note: Vous devriez idéalement chercher dans les tables patient, medecin, et admin.
        # Pour simplifier, nous utilisons seulement la table 'patient' ici.
        
        # 2. Exécution de la requête
        user = db.fetch_one(query, (email, password))
        
        if user:
            # --- Connexion réussie : Configuration de la session ---
            session['user_id'] = user['id']
            # Définissez le rôle (doit venir de la colonne 'role' de votre BDD ou être déduit)
            session['user_role'] = user.get('role', 'patient') 
            session['user_name'] = user['nom']
            flash(f"Connexion réussie ! Bienvenue, {user['nom']}.", 'success')
            
            # 3. Redirection basée sur le rôle
            if session['user_role'] == 'patient':
                return redirect(url_for('patient.accueil')) 
            # Ajoutez ici les redirections pour 'medecin' et 'admin'
            # elif session['user_role'] == 'medecin':
            #     return redirect(url_for('medecin.accueil'))

        else:
            # Échec de la connexion
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
        
        # 🚨 Logique BDD : Enregistrez le nouvel utilisateur
        
        # 1. Requête pour insérer le nouveau patient (Le mot de passe devrait être HACHÉ !)
        insert_query = """
        INSERT INTO patient (nom, email, password, role) 
        VALUES (%s, %s, %s, 'patient')
        """
        # 2. Exécution de la requête
        success = db.execute_query(insert_query, (nom, email, password))
        
        if success:
            flash('Inscription réussie ! Veuillez vous connecter.', 'success')
            return redirect(url_for('auth.login'))
        else:
            # Cela peut arriver si l'email existe déjà (si vous avez une contrainte UNIQUE)
            flash("Erreur lors de l'inscription. L'email existe peut-être déjà.", 'error')
            
    return render_template('auth/register.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('user_name', None)
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))