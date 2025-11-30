from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash("Accès refusé", "danger")
        return redirect(url_for('auth.login'))
    return render_template('admin/dashboard.html')

# Exemple de route pour approuver les médecins
@admin.route('/approve_medecin/<int:user_id>')
@login_required
def approve_medecin(user_id):
    if current_user.role != 'admin':
        flash("Accès refusé", "danger")
        return redirect(url_for('auth.login'))

    from app.models import User
    from app.extensions import db

    medecin = User.query.get(user_id)
    if medecin and medecin.role == 'medecin':
        medecin.approved = True
        db.session.commit()
        flash(f"Le médecin {medecin.fullname} a été approuvé.", "success")
    return redirect(url_for('admin.dashboard'))
