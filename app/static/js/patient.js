console.log("✅ patient.js est chargé avec succès !");

// DEBUG: Afficher tous les rendez-vous et leurs statuts
console.log('📋 Tous les rendez-vous:', appointments);
console.log('🔍 Statuts uniques trouvés:', [...new Set(appointments.map(a => a.status))]);

let currentFilter = 'tous';
let searchQuery = '';

// Fonction pour normaliser les statuts
function normalizeStatus(status) {
    const statusMap = {
        'confirmé': 'confirmé',
        'Confirmé': 'confirmé',
        'en attente': 'En attente', 
        'En attente': 'En attente',
        'terminé': 'terminé',
        'Terminé': 'terminé',
        'annulé': 'annulé',
        'Annulé': 'annulé'
    };
    return statusMap[status] || status;
}

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
        status: "En attente", // CORRECTION: Utiliser "En attente" pour la cohérence
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
    
                <input type="text" id="editClinic" value="${appointment.clinic}">
               Notes: <textarea id="editNotes">${appointment.notes || ''}</textarea>
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

// Stats - VERSION CORRIGÉE
function updateStats() {
    const statsEl = document.getElementById('stats');
    if (!statsEl) return;
    
    // Utiliser les statuts normalisés pour le comptage
    const normalizedAppointments = appointments.map(a => ({
        ...a,
        normalizedStatus: normalizeStatus(a.status)
    }));
    
    const total = normalizedAppointments.length;
    const confirmes = normalizedAppointments.filter(a => a.normalizedStatus === 'confirmé').length;
    const termines = normalizedAppointments.filter(a => a.normalizedStatus === 'terminé').length;
    const annules = normalizedAppointments.filter(a => a.normalizedStatus === 'annulé').length;
    const enAttente = normalizedAppointments.filter(a => a.normalizedStatus === 'En attente').length;

    console.log('📊 Statistiques calculées:', { total, confirmes, termines, annules, enAttente });

    statsEl.innerHTML = `
        <div class="stat-item">Total: ${total}</div>
        <div class="stat-item">Confirmés: ${confirmes}</div>
        <div class="stat-item">Terminés: ${termines}</div>
        <div class="stat-item">Annulés: ${annules}</div>
        <div class="stat-item">En attente: ${enAttente}</div>
    `;
}

// Render cards - VERSION CORRIGÉE
function renderAppointments() {
    const grid = document.getElementById('appointmentsGrid');
    const empty = document.getElementById('emptyState');
    if (!grid || !empty) return;

    // Normaliser les statuts pour le filtrage
    const normalizedAppointments = appointments.map(a => ({
        ...a,
        normalizedStatus: normalizeStatus(a.status)
    }));

    let filtered = normalizedAppointments;
    
    // CORRECTION: Filtrage avec statuts normalisés
    if (currentFilter !== 'tous') {
        const normalizedFilter = normalizeStatus(currentFilter);
        filtered = filtered.filter(a => a.normalizedStatus === normalizedFilter);
    }
    
    if (searchQuery) {
        filtered = filtered.filter(a =>
            a.medecin_name.toLowerCase().includes(searchQuery) ||
            a.medecin_spec.toLowerCase().includes(searchQuery) ||
            a.date.includes(searchQuery)
        );
    }

    console.log('🔍 Rendez-vous filtrés:', filtered);
    console.log('🎯 Filtre appliqué:', currentFilter);

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
        card.dataset.statut = a.normalizedStatus;

        // CORRECTION: Affichage cohérent du statut
        const statusDisplay = a.normalizedStatus;

        // CORRECTION: Logique des boutons avec statuts normalisés
        const showModifier = !(a.normalizedStatus === 'terminé' || a.normalizedStatus === 'annulé');
        const showAnnuler = (a.normalizedStatus === 'En attente' || a.normalizedStatus === 'confirmé');

      // Dans renderAppointments(), remplacez toute la partie card.innerHTML par :
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
        <span class="status ${a.normalizedStatus === 'En attente' ? 'en-attente' : a.normalizedStatus}">${statusDisplay}</span>
        <div class="card-actions">
            ${showModifier ? `<button class="btn-modifier" onclick="modifier(${a.id})">Modifier</button>` : ''}
            ${showAnnuler ? `<button class="btn-annuler" onclick="cancelAppointment(${a.id})">Annuler</button>` : ''}
        </div>
    </div>
`;
        grid.appendChild(card);
    });
}

// Filtres & recherche
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Initialisation du tableau de bord...");

    const filterButtons = document.querySelectorAll(".filter-btn");
    const searchInput = document.getElementById("searchInput");

    filterButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            filterButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentFilter = btn.dataset.filter;
            console.log('🎛️ Filtre changé:', currentFilter);
            renderAppointments();
            updateStats();
        });
    });

    searchInput.addEventListener("input", e => {
        searchQuery = e.target.value.toLowerCase();
        renderAppointments();
        updateStats();
    });

    // Initialisation
    renderAppointments();
    updateStats();
});

// Fonction de débogage
function debugStats() {
    console.log('🐛 Débogage détaillé:');
    appointments.forEach((rdv, index) => {
        console.log(`RDV ${index + 1}:`, {
            id: rdv.id,
            medecin: rdv.medecin_name,
            statut_original: rdv.status,
            statut_normalisé: normalizeStatus(rdv.status)
        });
    });
}