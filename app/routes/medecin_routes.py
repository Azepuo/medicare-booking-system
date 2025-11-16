# app/routes/medecins.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.connection import create_connection

medecins_bp = Blueprint("medecins_bp", __name__)

# ---------- LISTE DES MEDECINS ----------
@medecins_bp.route("/", methods=["GET"])
def liste_medecins():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM medecins")
    medecins = cursor.fetchall()

    cursor.close()
    conn.close()

    # adapte le nom du template à ton fichier
    return render_template("admin/medecins.html", medecins=medecins)


# ---------- FORMULAIRE AJOUT ----------
@medecins_bp.route("/add", methods=["GET", "POST"])
def ajouter_medecin():
    if request.method == "POST":
        nom = request.form.get("nom_complet")
        email = request.form.get("email")
        telephone = request.form.get("telephone")
        specialite = request.form.get("specialite")
        annees_experience = request.form.get("annees_experience") or None
        tarif = request.form.get("tarif_consultation") or None
        description = request.form.get("description")
        statut = request.form.get("statut")
        date_inscription = request.form.get("date_inscription") or None

        conn = create_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO medecins
            (nom, email, telephone, specialite,
             annees_experience, tarif_consultation, description, statut,
             date_inscription)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            nom, email, telephone, specialite,
            annees_experience, tarif, description, statut,
            date_inscription
        ))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Médecin ajouté avec succès", "success")
        return redirect(url_for("medecins_bp.liste_medecins"))

    # GET → afficher le formulaire
    return render_template("admin/medecin_add.html")


# ---------- FORMULAIRE EDIT ----------
@medecins_bp.route("/<int:medecin_id>/edit", methods=["GET", "POST"])
def editer_medecin(medecin_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    # récupérer le médecin
    cursor.execute("SELECT * FROM medecins WHERE id = %s", (medecin_id,))
    medecin = cursor.fetchone()

    if not medecin:
        cursor.close()
        conn.close()
        flash("Médecin introuvable", "error")
        return redirect(url_for("medecins_bp.liste_medecins"))

    if request.method == "POST":
        nom = request.form.get("nom_complet")
        email = request.form.get("email")
        telephone = request.form.get("telephone")
        specialite = request.form.get("specialite")
        annees_experience = request.form.get("annees_experience") or None
        tarif = request.form.get("tarif_consultation") or None
        description = request.form.get("description")
        statut = request.form.get("statut")
        date_inscription = request.form.get("date_inscription") or None

        sql = """
            UPDATE medecins
            SET nom=%s, email=%s, telephone=%s, specialite=%s,
                annees_experience=%s, tarif_consultation=%s,
                description=%s, statut=%s, date_inscription=%s
            WHERE id=%s
        """
        cursor.execute(sql, (
            nom, email, telephone, specialite,
            annees_experience, tarif, description, statut,
            date_inscription, medecin_id
        ))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Médecin modifié avec succès", "success")
        return redirect(url_for("medecins_bp.liste_medecins"))

    cursor.close()
    conn.close()
    # GET → afficher le formulaire pré-rempli
    return render_template("admin/medecin_edit.html", medecin=medecin)


# ---------- SUPPRESSION ----------
@medecins_bp.route("/<int:medecin_id>/delete", methods=["GET"])
def supprimer_medecin(medecin_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM medecins WHERE id = %s", (medecin_id,))
    conn.commit()

    cursor.close()
    conn.close()
    flash("Médecin supprimé avec succès", "success")

    return redirect(url_for("medecins_bp.liste_medecins"))
