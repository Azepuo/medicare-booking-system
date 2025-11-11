console.log("✅ patient.js est chargé avec succès !");

// === Données fictives ===
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

// === Fonctions utilitaires ===
const getInitials = (name) =>
    name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();

const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
};

// === Fonctions pour formulaire d'ajout ===
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

function addNewAppointment(patientName, patientAge, doctor, appointmentDate, appointmentTime, reason) {
    // Dictionnaires pour retrouver les infos du médecin
    const doctorNames = {
        dr_dupont: "Dr. Dupont",
        dr_martin: "Dr. Martin",
        dr_leroy: "Dr. Leroy",
        dr_bernard: "Dr. Bernard",
    };

    const doctorSpecs = {
        dr_dupont: "Cardiologie",
        dr_martin: "Dermatologie",
        dr_leroy: "Pédiatrie",
        dr_bernard: "Neurologie",
    };

    // Création du nouvel objet rendez-vous
    const newAppointment = {
        id: appointments.length + 1,
        medecin_name: doctorNames[doctor] || "Médecin inconnu",
        medecin_spec: doctorSpecs[doctor] || "Spécialité non définie",
        date: appointmentDate,
        time: appointmentTime,
        clinic: "Clinique Principale",
        notes: reason || "",
        status: "confirmé",
    };

    // Ajout dans la liste
    appointments.push(newAppointment);

    // Rafraîchir l'affichage
    renderAppointments();
    updateStats();
    hideAppointmentForm();

    alert('Rendez-vous ajouté avec succès!');
}

// === Fonctions globales pour les boutons ===
function modifier(id) {
    console.log("Modifier appelé pour ID:", id);
    const appointment = appointments.find(apt => apt.id === id);
    if (!appointment) {
        console.error("Rendez-vous non trouvé pour ID:", id);
        return;
    }

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

// === Mise à jour statistiques ===
function updateStats() {
    const statsEl = document.getElementById('stats');
    if (!statsEl) return;

    const total = appointments.length;
    const confirmed = appointments.filter(a => a.status === 'confirmé').length;
    const done = appointments.filter(a => a.status === 'terminé').length;
    const cancelled = appointments.filter(a => a.status === 'annulé').length;

    statsEl.innerHTML = `
        <div class="stat-card"><div class="stat-number">${total}</div><div class="stat-label">Total</div></div>
        <div class="stat-card"><div class="stat-number">${confirmed}</div><div class="stat-label">Confirmés</div></div>
        <div class="stat-card"><div class="stat-number">${done}</div><div class="stat-label">Terminés</div></div>
        <div class="stat-card"><div class="stat-number">${cancelled}</div><div class="stat-label">Annulés</div></div>
    `;
}

// === Affichage rendez-vous ===
function renderAppointments() {
    const grid = document.getElementById('appointmentsGrid');
    const emptyState = document.getElementById('emptyState');
    if (!grid || !emptyState) return;

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
                <div>📅 ${formatDate(apt.date)}</div>
                <div>🕐 ${apt.time}</div>
            </div>

            ${apt.notes ? `<div class="appointment-notes">${apt.notes}</div>` : ''}

            <div class="card-footer">
                <div class="clinic-name">${apt.clinic}</div>
                <div class="card-actions">
                    ${apt.status === 'confirmé'
            ? `<button class="btn btn-outline" onclick="cancelAppointment(${apt.id})">Annuler</button>` : ''}
                    <button class="btn btn-primary" onclick="modifier(${apt.id})">Modifier</button>
                </div>
            </div>
        </div>
    `).join('');
}

document.addEventListener('DOMContentLoaded', function () {
    console.log("✅ DOM entièrement chargé !");

    // === Filtres & recherche ===
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

    // === Gestion du formulaire d'ajout ===
    const appointmentForm = document.getElementById('appointmentForm');
    if (appointmentForm) {
        appointmentForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const patientName = document.getElementById("patientName").value.trim();
            const patientAge = document.getElementById("patientAge").value;
            const doctor = document.getElementById("doctor").value;
            const appointmentDate = document.getElementById("appointmentDate").value;
            const appointmentTime = document.getElementById("appointmentTime").value;
            const reason = document.getElementById("reason").value.trim();

            if (!patientName || !doctor || !appointmentDate || !appointmentTime) {
                alert("⚠️ Veuillez remplir tous les champs obligatoires.");
                return;
            }

            // Utiliser la fonction globale pour ajouter le rendez-vous
            addNewAppointment(patientName, patientAge, doctor, appointmentDate, appointmentTime, reason);

            // Réinitialiser le formulaire
            appointmentForm.reset();
        });

        // Définir la date minimale (pas de date passée)
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
            if (e.target === this) hideAppointmentForm();
        });
    }

    // Empêcher la fermeture en cliquant dans le formulaire
    const appointmentFormEl = document.querySelector('.appointment-form');
    if (appointmentFormEl) {
        appointmentFormEl.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    }

    // === Logout (sécurisé) ===
    const logoutTab = document.getElementById('LogoutTab');
    if (logoutTab) {
        logoutTab.addEventListener('click', function (e) {
            e.preventDefault();
            if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
                localStorage.clear();
                sessionStorage.clear();
                window.location.href = '/login';
            }
        });
    }

    // === Initialisation ===
    updateStats();
    renderAppointments();
});



document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const mainTitle = document.getElementById('mainTitle');
    
    if (currentPath.includes('/mes_rdv') || currentPath.includes('/rendezvous')) {
        if (mainTitle) mainTitle.textContent = 'Rendez-vous';
        document.title = 'Rendez-vous';
        activateNavTab('rendezvousTab');
    } 
    else {
        // Page par défaut (dashboard)
        if (mainTitle) mainTitle.textContent = 'Tableau de bord';
        document.title = 'Tableau de bord ';
        activateNavTab('dashboardTab');
    }
});

function activateNavTab(tabId) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeTab = document.getElementById(tabId);
    if (activeTab) {
        activeTab.classList.add('active');
    }
}