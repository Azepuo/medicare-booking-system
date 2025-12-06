from flask import Blueprint, render_template
from app.auth_rpc.decorators import role_required

admin = Blueprint("admin", __name__, url_prefix="/admin")

# 🔹 Dashboard
@admin.route("/dashboard")
@role_required("admin")
def dashboard():
    return render_template("admin/dashboard.html")

# 🔹 Gestion des médecins
@admin.route("/medecins")
@role_required("admin")
def medecins():
    return render_template("admin/medecins.html")

@admin.route("/medecin_add")
@role_required("admin")
def medecin_add():
    return render_template("admin/medecin_add.html")

@admin.route("/medecin_edit")
@role_required("admin")
def medecin_edit():
    return render_template("admin/medecin_edit.html")

# 🔹 Gestion des patients
@admin.route("/patients")
@role_required("admin")
def patients():
    return render_template("admin/patients.html")

@admin.route("/patient_add")
@role_required("admin")
def patient_add():
    return render_template("admin/patient_add.html")

@admin.route("/patient_edit")
@role_required("admin")
def patient_edit():
    return render_template("admin/patient_edit.html")

# 🔹 Facturation
@admin.route("/facturation")
@role_required("admin")
def facturation():
    return render_template("admin/facturation.html")

@admin.route("/facture_view")
@role_required("admin")
def facture_view():
    return render_template("admin/facture_view.html")

@admin.route("/facture_add")
@role_required("admin")
def facture_add():
    return render_template("admin/facture_add.html")

@admin.route("/facturation_edit")
@role_required("admin")
def facturation_edit():
    return render_template("admin/facturation_edit.html")

# 🔹 Rendez-vous
@admin.route("/rendez_vous")
@role_required("admin")
def rendez_vous():
    return render_template("admin/rendez_vous.html")

@admin.route("/rdv_add")
@role_required("admin")
def rdv_add():
    return render_template("admin/rdv_add.html")

@admin.route("/rdv_edit")
@role_required("admin")
def rdv_edit():
    return render_template("admin/rdv_edit.html")

# 🔹 Compte admin
@admin.route("/account")
@role_required("admin")
def account():
    return render_template("admin/account.html")

@admin.route("/update_admin")
@role_required("admin")
def update_admin():
    return render_template("admin/update_info_admin.html")

