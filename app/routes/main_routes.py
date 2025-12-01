# app/routes/main_routes.py
from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/services')
def services():
    return render_template('services.html')

@main.route('/about')
def about():
    return render_template('about.html')
