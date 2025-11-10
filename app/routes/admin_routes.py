from flask import Blueprint, render_template

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/dashboard")
def dashboard():
    return render_template("admin/dashboard.html")

@admin.route("/medecins")
def medecins():
    return render_template("admin/medecins.html")

@admin.route("/patients")
def patients():
    return render_template("admin/patients.html")

@admin.route("/facturation")
def facturation():
    return render_template("admin/facturation.html")

@admin.route("/facture_view")
def facture_view():
    return render_template("admin/facture_view.html")

@admin.route("/rendez_vous")
def rendez_vous():
    return render_template("admin/rendez_vous.html")

@admin.route("/account")
def account():
    return render_template("admin/account.html")

@admin.route("/update_admin")
def update_admin():
    return render_template("admin/update_info_admin.html")

@admin.route("/patient_add")
def patient_add():
    return render_template("admin/patient_add.html")

@admin.route("/medecin_add")
def medecin_add():
    return render_template("admin/medecin_add.html")

@admin.route("/facture_add")
def facture_add():
    return render_template("admin/facture_add.html")

@admin.route("/rdv_add")
def rdv_add():
    return render_template("admin/rdv_add.html")

@admin.route("/patient_edit")
def patient_edit():
    return render_template("admin/patient_edit.html")

@admin.route("/medecin_edit")
def medecin_edit():
    return render_template("admin/medecin_edit.html")

@admin.route("/rdv_edit")
def rdv_edit():
    return render_template("admin/rdv_edit.html")

@admin.route("/facturation_edit")
def facturation_edit():
    return render_template("admin/facturation_edit.html")
