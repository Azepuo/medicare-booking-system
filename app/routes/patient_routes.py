# Fichier : app/routes/patient_routes.py

from flask import Blueprint, render_template, session, redirect, url_for, flash
# (Assurez-vous que le décorateur login_required est défini ou importé ici)
# from .decorators import login_required 

patient = Blueprint('patient', __name__)

