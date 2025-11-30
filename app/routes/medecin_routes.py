from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

medecin = Blueprint('medecin', __name__, url_prefix='/medecin')

@medecin.route('/dashboard')
@login_required
def dashboard():
    # Vérification que seul un médecin approuvé peut accéder
    if current_user.role != 'medecin':
        flash("Accès refusé. Cette page est réservée aux médecins.", "danger")
        return redirect(url_for('auth.login'))
    
    if not current_user.approved:
        flash("Votre compte médecin n'a pas encore été approuvé par l'administrateur.", "warning")
        return redirect(url_for('auth.login'))

    return render_template('medecin/dashboard.html')
