const appointments = [
    { id: 1, date: "2025-11-08", time: "09:00", medecin_name: "Doctor1", medecin_spec: "specialite1", status: "terminé", clinic: "Adresse1" },
    { id: 2, date: "2025-11-10", time: "15:00", medecin_name: "Doctor2", medecin_spec: "specialite2", status: "confirmé", clinic: "Adresse2" },
    { id: 3, date: "2025-12-02", time: "11:30", medecin_name: "Doctor3", medecin_spec: "specialite3", status: "annulé", clinic: "Adresse3" },
    { id: 4, date: "2025-10-25", time: "16:00", medecin_name: "Doctor4", medecin_spec: "specialite4", status: "terminé", clinic: "Adresse4" },
    { id: 5, date: "2025-11-15", time: "10:30", medecin_name: "Doctor5", medecin_spec: "specialite5", status: "confirmé", clinic: "Adresse5" },
    { id: 6, date: "2025-09-20", time: "14:00", medecin_name: "Doctor6", medecin_spec: "specialite6", status: "terminé", clinic: "Adresse6" },
    { id: 7, date: "2025-09-20", time: "14:00", medecin_name: "Doctor7", medecin_spec: "specialite7", status: "terminé", clinic: "Adresse7" }
];

let currentFilter = 'tous';
let searchQuery = '';

function getInitials(name) {
    return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
}

function updateStats() {
    const statsEl = document.getElementById('stats');
    if (!statsEl) return;

    const total = appointments.length;
    const confirmed = appointments.filter(a => a.status === 'confirmé').length;
    const done = appointments.filter(a => a.status === 'terminé').length;
    const cancelled = appointments.filter(a => a.status === 'annulé').length;

    statsEl.innerHTML = `
        <div class="stat-card">
            <div class="stat-number">${total}</div>
            <div class="stat-label">Total</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${confirmed}</div>
            <div class="stat-info">Confirmés</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${done}</div>
            <div class="stat-label">Terminés</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${cancelled}</div>
            <div class="stat-label">Annulés</div>
        </div>
    `;
}

function renderAppointments() {
    let filtered = appointments;

    if (currentFilter !== 'tous') {
        filtered = filtered.filter(a => a.status === currentFilter);
    }

    if (searchQuery) {
        filtered = filtered.filter(a =>
            a.medecin_name.toLowerCase().includes(searchQuery) ||
            a.medecin_spec.toLowerCase().includes(searchQuery) ||
            a.date.includes(searchQuery) ||
            a.clinic.toLowerCase().includes(searchQuery)
        );
    }

    const grid = document.getElementById('appointmentsGrid');
    const emptyState = document.getElementById('emptyState');

    if (!grid || !emptyState) return;

    if (filtered.length === 0) {
        grid.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    grid.style.display = 'grid';
    emptyState.style.display = 'none';

    grid.innerHTML = filtered.map(apt => `
        <div class="appointment-card">
          <div class="card-header">
            <div class="doctor-info">
              <div class="avatar">${getInitials(apt.medecin_name)}</div>
              <div class="doctor-details">
                <h3>${apt.medecin_name}</h3>
                <p>${apt.medecin_spec}</p>
              </div>
            </div>
            <span class="status-badge ${apt.status}">${apt.status}</span>
          </div>
          
          <div class="appointment-datetime">
            <div class="datetime-item">
              <span>📅</span>
              <span>${formatDate(apt.date)}</span>
            </div>
            <div class="datetime-item">
              <span>🕐</span>
              <span>${apt.time}</span>
            </div>
          </div>
          
          ${apt.notes ? `<div class="appointment-notes">${apt.notes}</div>` : ''}
          
          <div class="card-footer">
            <div class="clinic-name">${apt.clinic}</div>
            <div class="card-actions">
              ${apt.status === 'confirmé' ? `
                <button class="btn btn-outline" onclick="cancelAppointment(${apt.id})">Annuler</button>
              ` : ''}
              <button class="btn btn-primary" onclick="modifier(${apt.id})">modifier</button>
            </div>
          </div>
        </div>
      `).join('');
}

function modifier(id) {
    const appointment = appointments.find(apt => apt.id === id);
    if (!appointment) return;

    const editFormHTML = `
        <div class="edit-form-container" id="editFormContainer">
            <div class="edit-form">
                <div class="edit-form-header">
                    <h2 class="edit-form-title">Modifier le Rendez-vous</h2>
                    <button class="edit-close-form" onclick="hideEditForm()">&times;</button>
                </div>
                <form id="editAppointmentForm">
                    <input type="hidden" id="editId" value="${appointment.id}">
                    
                    <div class="edit-form-row">
                        <div class="edit-form-group">
                            <label for="editMedecinName">Nom du Médecin</label>
                            <input type="text" id="editMedecinName" class="edit-form-control" value="${appointment.medecin_name}" required>
                        </div>
                        <div class="edit-form-group">
                            <label for="editMedecinSpec">Spécialité</label>
                            <input type="text" id="editMedecinSpec" class="edit-form-control" value="${appointment.medecin_spec}" required>
                        </div>
                    </div>

                    <div class="edit-form-row">
                        <div class="edit-form-group">
                            <label for="editDate">Date</label>
                            <input type="date" id="editDate" class="edit-form-control" value="${appointment.date}" required>
                        </div>
                        <div class="edit-form-group">
                            <label for="editTime">Heure</label>
                            <input type="time" id="editTime" class="edit-form-control" value="${appointment.time}" required>
                        </div>
                    </div>

                    <div class="edit-form-group">
                        <label for="editStatus">Statut</label>
                        <select id="editStatus" class="edit-form-control" required>
                            <option value="confirmé" ${appointment.status === 'confirmé' ? 'selected' : ''}>Confirmé</option>
                            <option value="terminé" ${appointment.status === 'terminé' ? 'selected' : ''}>Terminé</option>
                            <option value="annulé" ${appointment.status === 'annulé' ? 'selected' : ''}>Annulé</option>
                        </select>
                    </div>

                    <div class="edit-form-group">
                        <label for="editClinic">Clinique</label>
                        <input type="text" id="editClinic" class="edit-form-control" value="${appointment.clinic}" required>
                    </div>

                    <div class="edit-form-group">
                        <label for="editNotes">Notes (optionnel)</label>
                        <textarea id="editNotes" class="edit-form-control" rows="3" placeholder="Notes supplémentaires...">${appointment.notes || ''}</textarea>
                    </div>

                    <div class="edit-form-actions">
                        <button type="button" class="edit-btn-cancel" onclick="hideEditForm()">Annuler</button>
                        <button type="submit" class="edit-btn-submit">Enregistrer les modifications</button>
                    </div>
                </form>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', editFormHTML);

    document.getElementById('editAppointmentForm').addEventListener('submit', function (e) {
        e.preventDefault();
        saveAppointmentChanges(id);
    });

    document.getElementById('editFormContainer').style.display = 'flex';
}

function hideEditForm() {
    const editForm = document.getElementById('editFormContainer');
    if (editForm) {
        editForm.remove();
    }
}

function saveAppointmentChanges(id) {
    const medecinName = document.getElementById('editMedecinName').value;
    const medecinSpec = document.getElementById('editMedecinSpec').value;
    const date = document.getElementById('editDate').value;
    const time = document.getElementById('editTime').value;
    const status = document.getElementById('editStatus').value;
    const clinic = document.getElementById('editClinic').value;
    const notes = document.getElementById('editNotes').value;

    if (!medecinName || !medecinSpec || !date || !time || !status || !clinic) {
        alert('Veuillez remplir tous les champs obligatoires');
        return;
    }

    const appointmentIndex = appointments.findIndex(apt => apt.id === id);
    if (appointmentIndex === -1) return;

    appointments[appointmentIndex] = {
        ...appointments[appointmentIndex],
        medecin_name: medecinName,
        medecin_spec: medecinSpec,
        date: date,
        time: time,
        status: status,
        clinic: clinic,
        notes: notes
    };

    alert('Rendez-vous modifié avec succès!');
    hideEditForm();
    updateStats();
    renderAppointments();
}

function cancelAppointment(id) {
    if (confirm('Êtes-vous sûr de vouloir annuler ce rendez-vous ?')) {
        const appointmentIndex = appointments.findIndex(apt => apt.id === id);
        if (appointmentIndex !== -1) {
            appointments[appointmentIndex].status = 'annulé';
            updateStats();
            renderAppointments();
            alert('Rendez-vous annulé avec succès!');
        }
    }
}

function showAppointmentForm() {
    const formContainer = document.getElementById('appointmentFormContainer');
    if (formContainer) {
        formContainer.style.display = 'flex';
    }
}

function hideAppointmentForm() {
    const formContainer = document.getElementById('appointmentFormContainer');
    if (formContainer) {
        formContainer.style.display = 'none';
    }
}

// Gestion de la navigation entre les onglets
document.addEventListener('DOMContentLoaded', function () {
    const dashboardTab = document.getElementById('dashboardTab');
    const rendezvousTab = document.getElementById('rendezvousTab');
    const accountTab = document.getElementById('accountTab');

    const mainHeader = document.getElementById('mainHeader');
    const dashboardContent = document.getElementById('dashboardContent');
    const rendezvousContent = document.getElementById('rendezvousContent');
    const accountContent = document.getElementById('accountContent');

    // Initialiser les événements de recherche et filtres
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.toLowerCase();
            renderAppointments();
        });
    }

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderAppointments();
        });
    });

    // Gestion du formulaire d'ajout de rendez-vous
    const appointmentForm = document.getElementById('appointmentForm');
    if (appointmentForm) {
        appointmentForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const patientName = document.getElementById('patientName').value;
            const patientAge = document.getElementById('patientAge').value;
            const doctor = document.getElementById('doctor').value;
            const appointmentDate = document.getElementById('appointmentDate').value;
            const appointmentTime = document.getElementById('appointmentTime').value;
            const reason = document.getElementById('reason').value;

            if (!patientName || !patientAge || !doctor || !appointmentDate || !appointmentTime) {
                alert('Veuillez remplir tous les champs obligatoires');
                return;
            }

            const doctorOption = document.querySelector(`#doctor option[value="${doctor}"]`);
            const newAppointment = {
                id: appointments.length + 1,
                medecin_name: doctorOption.textContent.split(' (')[0],
                medecin_spec: doctorOption.textContent.match(/\((.*?)\)/)[1],
                date: appointmentDate,
                time: appointmentTime,
                status: "confirmé",
                clinic: "Adresse à définir",
                notes: reason || ""
            };

            appointments.push(newAppointment);

            alert('Rendez-vous pris avec succès!');
            this.reset();
            hideAppointmentForm();
            updateStats();
            renderAppointments();
        });

        // Définir la date minimale
        const today = new Date().toISOString().split('T')[0];
        const dateInput = document.getElementById('appointmentDate');
        if (dateInput) {
            dateInput.setAttribute('min', today);
        }
    }

    // Fermer le formulaire en cliquant à l'extérieur
    const appointmentFormContainer = document.getElementById('appointmentFormContainer');
    if (appointmentFormContainer) {
        appointmentFormContainer.addEventListener('click', function (e) {
            if (e.target === this) {
                hideAppointmentForm();
            }
        });
    }

    const appointmentFormEl = document.querySelector('.appointment-form');
    if (appointmentFormEl) {
        appointmentFormEl.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    }

    // Dashboard par défaut
    if (dashboardTab && rendezvousTab && accountTab) {
        showDashboard();

        dashboardTab.addEventListener('click', function (e) {
            e.preventDefault();
            showDashboard();
        });

        rendezvousTab.addEventListener('click', function (e) {
            e.preventDefault();
            showRendezvous();
        });

        accountTab.addEventListener('click', function (e) {
            e.preventDefault();
            showAccount();
        });
    }

    // Gestion du formulaire d'informations personnelles
    const personalInfoForm = document.getElementById('personalInfoForm');
    if (personalInfoForm) {
        personalInfoForm.addEventListener('submit', function (e) {
            e.preventDefault();
            alert('Informations mises à jour avec succès!');
            cancelEdit('personalInfo');
        });
    }
});

function showDashboard() {
    document.querySelectorAll('.content').forEach(content => {
        content.style.display = 'none';
    });

    const dashboardContent = document.getElementById('dashboardContent');
    const mainHeader = document.getElementById('mainHeader');

    if (dashboardContent) {
        dashboardContent.style.display = 'block';
    }

    if (mainHeader) {
        mainHeader.style.display = 'flex';
    }

    updateActiveNav('dashboardTab');

    const welcomeTitle = document.querySelector('.welcome-title');
    if (welcomeTitle) {
        welcomeTitle.textContent = 'Tableau de bord';
    }
}

function showRendezvous() {
    document.querySelectorAll('.content').forEach(content => {
        content.style.display = 'none';
    });

    const rendezvousContent = document.getElementById('rendezvousContent');
    const mainHeader = document.getElementById('mainHeader');

    if (rendezvousContent) {
        rendezvousContent.style.display = 'block';
    }

    if (mainHeader) {
        mainHeader.style.display = 'none';
    }

    updateActiveNav('rendezvousTab');

   

    updateStats();
    renderAppointments();
}

function showAccount() {
    // Cacher tout
    document.querySelectorAll('.content').forEach(content => {
        content.style.display = 'none';
    });

    // AJOUTER CETTE LIGNE pour cacher la barre de recherche et notifications
    const mainHeader = document.getElementById('mainHeader');
    if (mainHeader) {
        mainHeader.style.display = 'none';
    }

    // Afficher compte
    const accountContent = document.getElementById('accountContent');
    if (accountContent) {
        accountContent.style.display = 'block';
    }

    updateActiveNav('accountTab');

    const welcomeTitle = document.querySelector('.welcome-title');
    if (welcomeTitle) {
        welcomeTitle.textContent = 'Mon Compte';
    }
}

function updateActiveNav(activeId) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    const activeElement = document.getElementById(activeId);
    if (activeElement) {
        activeElement.classList.add('active');
    }
}

function toggleEdit(section) {
    const form = document.getElementById(section + 'Form');
    if (!form) return;

    const inputs = form.querySelectorAll('input, select');
    const actions = document.getElementById(section + 'Actions');

    inputs.forEach(input => {
        if (input.type !== 'checkbox') {
            input.readOnly = !input.readOnly;
        }
        input.disabled = !input.disabled;
    });

    if (actions) {
        actions.style.display = actions.style.display === 'none' ? 'flex' : 'none';
    }
}

function cancelEdit(section) {
    const form = document.getElementById(section + 'Form');
    if (!form) return;

    const inputs = form.querySelectorAll('input, select');
    const actions = document.getElementById(section + 'Actions');

    inputs.forEach(input => {
        input.readOnly = true;
        input.disabled = true;
    });

    if (actions) {
        actions.style.display = 'none';
    }

    form.reset();
}

function changePassword() {
    alert('Fonctionnalité de changement de mot de passe à implémenter');
}

const logoutTab = document.getElementById('LogoutTab');

logoutTab.addEventListener('click', function (e) {
    e.preventDefault();

    if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = 'login.html';//page de connexion


    }
});