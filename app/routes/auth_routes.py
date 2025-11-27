# app/routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
# Importez votre instance de connexion à la BDD
# from database.connection import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html')
@auth.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('auth/register.html')

@auth.route('/logout')
def logout():
    return redirect(url_for('auth.login'))
