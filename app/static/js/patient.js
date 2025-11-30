console.log("✅ patient.js est chargé avec succès !");

let currentFilter = 'tous';
let searchQuery = '';

// Fonctions utilitaires
const getInitials = name => name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
const formatDate = dateStr => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
};

// Formulaire ajout
function showAppointmentForm() {
    const formContainer = document.getElementById('appointmentFormContainer');
    if (formContainer) formContainer.style.display = 'flex';
}
function hideAppointmentForm() {
    const formContainer = document.getElementById('appointmentFormContainer');
    if (formContainer) formContainer.style.display = 'none';
}

// Ajouter un rendez-vous
function addNewAppointment(patientName, patientAge, doctor, appointmentDate, appointmentTime, reason) {
    const doctorNames = { dr_dupont: "Dr. Dupont" };
    const doctorSpecs = { dr_dupont: "Cardiologie" };

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

    appointments.push(newAppointment);
    renderAppointments();
    updateStats();
    hideAppointmentForm();
}

// Modifier rendez-vous
function modifier(id) {
    const appointment = appointments.find(a => a.id === id);
    if (!appointment) return;

    const editFormHTML = `
    <div class="edit-form-container" id="editFormContainer">
        <div class="edit-form">
            <form id="editAppointmentForm">
                <input type="hidden" id="editId" value="${appointment.id}">
                <input type="text" id="editMedecinName" value="${appointment.medecin_name}">
                <input type="text" id="editMedecinSpec" value="${appointment.medecin_spec}">
                <input type="date" id="editDate" value="${appointment.date}">
                <input type="time" id="editTime" value="${appointment.time}">
                <select id="editStatus">
                    <option value="confirmé" ${appointment.status === 'confirmé' ? 'selected' : ''}>Confirmé</option>
                    <option value="attente" ${appointment.status === 'attente' ? 'selected' : ''}>En attente</option>
                    <option value="terminé" ${appointment.status === 'terminé' ? 'selected' : ''}>Terminé</option>
                    <option value="annulé" ${appointment.status === 'annulé' ? 'selected' : ''}>Annulé</option>
                </select>
                <input type="text" id="editClinic" value="${appointment.clinic}">
                <textarea id="editNotes">${appointment.notes || ''}</textarea>
                <button type="submit">Enregistrer</button>
            </form>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', editFormHTML);
    document.getElementById('editAppointmentForm').addEventListener('submit', function (e) {
        e.preventDefault();
        saveAppointmentChanges(id);
    });
}

function saveAppointmentChanges(id) {
    const idx = appointments.findIndex(a => a.id === id);
    if (idx === -1) return;

    appointments[idx] = {
        ...appointments[idx],
        medecin_name: document.getElementById('editMedecinName').value,
        medecin_spec: document.getElementById('editMedecinSpec').value,
        date: document.getElementById('editDate').value,
        time: document.getElementById('editTime').value,
        status: document.getElementById('editStatus').value,
        clinic: document.getElementById('editClinic').value,
        notes: document.getElementById('editNotes').value
    };

    hideEditForm();
    updateStats();
    renderAppointments();
}

function hideEditForm() {
    const f = document.getElementById('editFormContainer');
    if (f) f.remove();
}

function cancelAppointment(id) {
    if (confirm('Êtes-vous sûr de vouloir annuler ce rendez-vous ?')) {
        const idx = appointments.findIndex(a => a.id === id);
        if (idx !== -1) {
            appointments[idx].status = 'annulé';
            renderAppointments();
            updateStats();
        }
    }
}

// Stats
function updateStats() {
    const statsEl = document.getElementById('stats');
    if (!statsEl) return;
    statsEl.innerHTML = `
        <div>Total: ${appointments.length}</div>
        <div>Confirmés: ${appointments.filter(a => a.status === 'confirmé').length}</div>
        <div>Terminés: ${appointments.filter(a => a.status === 'terminé').length}</div>
        <div>Annulés: ${appointments.filter(a => a.status === 'annulé').length}</div>
        <div>En attente: ${appointments.filter(a => a.status.toLowerCase() === 'attente').length}</div>
    `;
}

// Render cards
function renderAppointments() {
    const grid = document.getElementById('appointmentsGrid');
    const empty = document.getElementById('emptyState');
    if (!grid || !empty) return;

    let filtered = appointments;
    if (currentFilter !== 'tous') filtered = filtered.filter(a => a.status === currentFilter);
    if (searchQuery) filtered = filtered.filter(a =>
        a.medecin_name.toLowerCase().includes(searchQuery) ||
        a.medecin_spec.toLowerCase().includes(searchQuery) ||
        a.date.includes(searchQuery)
    );

    grid.innerHTML = '';
    if (filtered.length === 0) {
        grid.style.display = 'none';
        empty.style.display = 'block';
        return;
    }

    grid.style.display = 'grid';
    empty.style.display = 'none';

    filtered.forEach(a => {
        const card = document.createElement('div');
        card.classList.add('appointment-card');
        card.dataset.statut = a.status;
        
        // Afficher le statut en français
        const statusDisplay = a.status === 'attente' ? 'En attente' : a.status;
        
        card.innerHTML = `
            <div class="card-header">
                <h3>${a.medecin_name}</h3>
                <span class="specialite">${a.medecin_spec}</span>
            </div>
            <div class="card-body">
                <p><strong>Date :</strong> ${a.date} ${a.time}</p>
                <p><strong>Clinique :</strong> ${a.clinic}</p>
            </div>
            <div class="card-footer">
                <span class="status ${a.status}">${statusDisplay}</span>
                <div class="card-actions">
                    ${a.status === 'terminé' || a.status === 'annulé' ? '' : `<button class="btn-modifier" onclick="modifier(${a.id})">Modifier</button>`}
                    ${a.status === 'attente' || a.status === 'confirmé' ? `<button class="btn-annuler" onclick="cancelAppointment(${a.id})">Annuler</button>` : ''}
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Filtres & recherche
document.addEventListener("DOMContentLoaded", () => {
    const filterButtons = document.querySelectorAll(".filter-btn");
    const searchInput = document.getElementById("searchInput");

    filterButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            filterButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentFilter = btn.dataset.filter;
            renderAppointments();
            updateStats();
        });
    });

    searchInput.addEventListener("input", e => {
        searchQuery = e.target.value.toLowerCase();
        renderAppointments();
        updateStats();
    });

    renderAppointments();
    updateStats();
});