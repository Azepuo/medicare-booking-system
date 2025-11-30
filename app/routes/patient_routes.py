from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

patient = Blueprint('patient', __name__, url_prefix='/patient')

@patient.route('/dashboard')
@login_required
def dashboard():
    # Vérification que seul un patient peut accéder
    if current_user.role != 'patient':
        flash("Accès refusé. Cette page est réservée aux patients.", "danger")
        return redirect(url_for('auth.login'))

    return render_template('patient/dashboard.html')
