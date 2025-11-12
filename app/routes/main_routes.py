# app/routes/main_routes.py
from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Home page mapped to existing template
    return render_template('acceuil/index.html')

@main.route('/home')
def home():
    # Optional second landing page if needed
    return render_template('acceuil/accueil.html')
