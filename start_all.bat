@echo off
echo ===============================
echo Lancement de toutes les apps
echo ===============================

echo Admin (port 5003)
start cmd /k python -m app.app_admin

echo Medecin (port 5001)
start cmd /k python -m app.main_medecin

echo Patient (port 5002)
start cmd /k python -m app.patient_app

echo App generale (port 5000)
start cmd /k python app.py

echo ===============================
echo Toutes les apps sont lancees
echo ===============================
pause
