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
function modifier(appointment) {
    console.log('🔧 Modification du RDV:', appointment);
    console.log('⏰ Heure du RDV:', appointment.time, 'Type:', typeof appointment.time);
    
    const editFormHTML = `
    <div class="edit-form-container" id="editFormContainer">
        <div class="edit-form">
            <h3>Modifier le rendez-vous</h3>
            <form id="editAppointmentForm">
                <input type="hidden" id="editId" value="${appointment.id}">

                <label>Spécialisation</label>
                <select id="editSpecialization" required>
                    <option value="">Choisir une spécialisation</option>
                </select>

                <label>Docteur</label>
                <select id="editDoctor" required disabled>
                    <option value="">Sélectionnez une spécialisation d'abord</option>
                </select>

                <label>Date</label>
                <select id="editDate" required disabled>
                    <option value="">Sélectionnez un docteur d'abord</option>
                </select>

                <label>Heure</label>
                <select id="editTime" required disabled>
                    <option value="">Sélectionnez une date d'abord</option>
                </select>
                
                <label>Notes</label>
                <textarea id="editNotes" rows="3" placeholder="Notes supplémentaires...">${appointment.notes || ''}</textarea>

                <div class="form-buttons">
                    <button type="submit" class="btn-save">Enregistrer</button>
                    <button type="button" class="btn-cancel" onclick="hideEditForm()">Annuler</button>
                </div>
            </form>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', editFormHTML);

    const specSelect = document.getElementById('editSpecialization');
    const doctorSelect = document.getElementById('editDoctor');
    const dateSelect = document.getElementById('editDate');
    const timeSelect = document.getElementById('editTime');

    // Remplir spécialisations
    specialisations.forEach(s => {
        const option = document.createElement('option');
        option.value = s[0];
        option.textContent = s[1];
        if (appointment.medecin_spec === s[1]) {
            option.selected = true;
        }
        specSelect.appendChild(option);
    });

    // Event: Changement de spécialisation
    specSelect.addEventListener('change', function() {
        const spec_id = this.value;
        console.log('📋 Spécialisation sélectionnée:', spec_id);
        
        doctorSelect.disabled = true;
        doctorSelect.innerHTML = '<option value="">Chargement...</option>';
        dateSelect.disabled = true;
        dateSelect.innerHTML = '<option value="">Sélectionnez un docteur d\'abord</option>';
        timeSelect.disabled = true;
        timeSelect.innerHTML = '<option value="">Sélectionnez une date d\'abord</option>';

        if (spec_id) {
            fetch(`/patient/get_doctors?specialization=${spec_id}`)
                .then(res => res.json())
                .then(data => {
                    console.log('👨‍⚕️ Docteurs reçus:', data);
                    doctorSelect.disabled = false;
                    doctorSelect.innerHTML = '<option value="">Sélectionnez un docteur</option>';
                    
                    data.forEach(d => {
                        const option = document.createElement('option');
                        option.value = d.id;
                        option.textContent = d.nom;
                        doctorSelect.appendChild(option);
                    });

                    // CORRECTION: Sélectionner le docteur APRÈS avoir rempli la liste
                    if (appointment.medecin_id) {
                        doctorSelect.value = appointment.medecin_id;
                        console.log('✅ Docteur défini:', appointment.medecin_id);
                        // Déclencher le chargement des dates
                        setTimeout(() => doctorSelect.dispatchEvent(new Event('change')), 100);
                    }
                })
                .catch(err => console.error('❌ Erreur chargement docteurs:', err));
        }
    });

    // Event: Changement de docteur
    doctorSelect.addEventListener('change', function() {
        const doctor_id = this.value;
        console.log('👨‍⚕️ Docteur sélectionné:', doctor_id);
        
        dateSelect.disabled = true;
        dateSelect.innerHTML = '<option value="">Chargement...</option>';
        timeSelect.disabled = true;
        timeSelect.innerHTML = '<option value="">Sélectionnez une date d\'abord</option>';

        if (doctor_id) {
            fetch(`/patient/get_available_dates?doctor_id=${doctor_id}`)
                .then(res => res.json())
                .then(data => {
                    console.log('📅 Dates reçues:', data);
                    dateSelect.disabled = false;
                    dateSelect.innerHTML = '<option value="">Sélectionnez une date</option>';
                    
                    if (data.dates && data.dates.length > 0) {
                        data.dates.forEach(d => {
                            const option = document.createElement('option');
                            option.value = d;
                            option.textContent = d;
                            dateSelect.appendChild(option);
                        });

                        // CORRECTION: Sélectionner la date APRÈS avoir rempli la liste
                        if (appointment.date) {
                            dateSelect.value = appointment.date;
                            console.log('✅ Date définie:', appointment.date);
                            // Déclencher le chargement des heures
                            setTimeout(() => dateSelect.dispatchEvent(new Event('change')), 100);
                        }
                    }
                })
                .catch(err => console.error('❌ Erreur chargement dates:', err));
        }
    });

    // Event: Changement de date
    dateSelect.addEventListener('change', function() {
        const doctor_id = doctorSelect.value;
        const consultation_date = this.value;
        console.log('📅 Date sélectionnée:', consultation_date);
        
        timeSelect.disabled = true;
        timeSelect.innerHTML = '<option value="">Chargement...</option>';

        if (doctor_id && consultation_date) {
            fetch(`/patient/get_available_slots?doctor_id=${doctor_id}&consultation_date=${consultation_date}`)
                .then(res => res.json())
                .then(data => {
                    console.log('⏰ Créneaux reçus:', data);
                    timeSelect.disabled = false;
                    timeSelect.innerHTML = '<option value="">Sélectionnez un créneau</option>';
                    
                    if (data.slots && data.slots.length > 0) {
                        console.log('🔍 Recherche de l\'heure:', appointment.time);
                        
                        data.slots.forEach(slot => {
                            const option = document.createElement('option');
                            option.value = slot;
                            option.textContent = slot;
                            timeSelect.appendChild(option);
                        });

                        // CORRECTION: Sélectionner l'heure APRÈS avoir rempli la liste
                        if (appointment.time) {
                            // Essayer de trouver l'heure exacte
                            let found = false;
                            for (let i = 0; i < timeSelect.options.length; i++) {
                                if (timeSelect.options[i].value === appointment.time) {
                                    timeSelect.value = appointment.time;
                                    found = true;
                                    console.log('✅ Heure sélectionnée:', appointment.time);
                                    break;
                                }
                            }
                            
                            if (!found) {
                                console.warn('⚠️ Heure non trouvée:', appointment.time);
                                console.log('Créneaux disponibles:', data.slots);
                            }
                        }
                    }
                })
                .catch(err => console.error('❌ Erreur chargement créneaux:', err));
        }
    });

    // Déclencher le chargement en cascade
    if (appointment.medecin_spec) {
        const spec = specialisations.find(s => s[1] === appointment.medecin_spec);
        if (spec) {
            specSelect.value = spec[0];
            setTimeout(() => specSelect.dispatchEvent(new Event('change')), 100);
        }
    }

    // Soumission du formulaire
    document.getElementById('editAppointmentForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const id = document.getElementById('editId').value;
        const medecin_id = document.getElementById('editDoctor').value;
        const date = document.getElementById('editDate').value;
        const time = document.getElementById('editTime').value;
        const notes = document.getElementById('editNotes').value;

        if (!medecin_id || !date || !time) {
            showToast("Veuillez remplir tous les champs", true);
            return;
        }

        const formData = new FormData();
        formData.append('id', id);
        formData.append('medecin_id', medecin_id);
        formData.append('date', date);
        formData.append('time', time);
        formData.append('notes', notes);

        fetch('/patient/update_appointment', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast("✅ Rendez-vous mis à jour !");
                hideEditForm();
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast("❌ " + (data.message || "Erreur"), true);
            }
        })
        .catch(err => {
            showToast("❌ Erreur serveur", true);
            console.error(err);
        });
    });
}

// Ajoutez la fonction showToast si elle n'existe pas
function showToast(message, isError = false) {
    // Créer un élément toast
    const toast = document.createElement('div');
    toast.className = `toast ${isError ? 'error' : 'success'}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${isError ? '#f44336' : '#4CAF50'};
        color: white;
        border-radius: 5px;
        z-index: 10000;
        animation: fadeIn 0.3s;
        font-family: Arial, sans-serif;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
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
        console.log(`🚫 Tentative d'annulation du RDV ${id}`);
        
        // Envoyer la requête au serveur
        fetch('/patient/cancel_appointment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ appointment_id: id })
        })
        .then(res => {
            console.log('Réponse reçue, statut:', res.status);
            if (!res.ok) {
                throw new Error('Erreur réseau: ' + res.status);
            }
            return res.json();
        })
        .then(data => {
            console.log('Réponse du serveur:', data);
            if (data.success) {
                // Mettre à jour le statut localement
                const idx = appointments.findIndex(a => a.id === id);
                if (idx !== -1) {
                    appointments[idx].status = 'Annulé';
                    renderAppointments();
                    updateStats();
                    showToast("✅ Rendez-vous annulé avec succès !");
                }
            } else {
                showToast("❌ Erreur: " + (data.message || "Échec de l'annulation"), true);
            }
        })
        .catch(err => {
            console.error('Erreur lors de l\'annulation:', err);
            showToast("❌ Erreur serveur lors de l'annulation", true);
        });
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
        <p><strong>Clinique :</strong> ${a.clinic || '-'}</p>
    </div>
    <div class="card-footer">
        <span class="status ${a.normalizedStatus === 'En attente' ? 'en-attente' : a.normalizedStatus.toLowerCase()}">${a.status}</span>
        <div class="card-actions">
            ${showModifier ? `<button class="btn-modifier" onclick='modifier(${JSON.stringify(a)})'>Modifier</button>` : ''}
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
// patient.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('Patient.js chargé');
    
    // Fonction pour mettre à jour le titre selon la page active
    function updatePageTitle() {
        const currentPath = window.location.pathname;
        const mainTitle = document.getElementById('mainTitle');
        
        if (!mainTitle) {
            console.error('Element mainTitle non trouvé');
            return;
        }
        
        console.log('Path actuel:', currentPath);
        
        // Déterminer le titre selon la route
        if (currentPath.includes('/mes_rdv') || currentPath.includes('/rendezvous')) {
            mainTitle.textContent = 'Mes Rendez-vous';
            console.log('Titre mis à jour: Mes Rendez-vous');
        } else if (currentPath.includes('/profile')) {
            mainTitle.textContent = 'Mon Profil';
            console.log('Titre mis à jour: Mon Profil');
        } else if (currentPath.includes('/dashboard') || currentPath === '/patient/' || currentPath === '/patient/dashboard') {
            mainTitle.textContent = 'Tableau de bord';
            console.log('Titre mis à jour: Tableau de bord');
        }
        
        // Mettre à jour aussi le titre de l'onglet
        document.title = mainTitle.textContent + ' - WeCare';
    }
    
    // Mettre à jour au chargement
    updatePageTitle();
    
    // Ajouter des écouteurs d'événements aux liens de navigation
    const navLinks = document.querySelectorAll('.nav-item');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            console.log('Lien cliqué:', this.href);
            
            // Pour les liens normaux (non-AJAX), on met à jour après un court délai
            if (!this.hasAttribute('data-ajax')) {
                setTimeout(updatePageTitle, 100);
            }
        });
    });
    
    // Mettre en évidence l'onglet actif
    function highlightActiveTab() {
        const currentPath = window.location.pathname;
        navLinks.forEach(link => {
            link.classList.remove('active');
            
            // Vérifier si le lien correspond à la page actuelle
            const linkPath = new URL(link.href).pathname;
            if (currentPath === linkPath || 
                (currentPath.includes('/mes_rdv') && linkPath.includes('/mes_rdv')) ||
                (currentPath.includes('/profile') && linkPath.includes('/profile')) ||
                (currentPath.includes('/dashboard') && linkPath.includes('/dashboard'))) {
                link.classList.add('active');
                console.log('Onglet actif:', link.querySelector('span').textContent);
            }
        });
    }
    
    highlightActiveTab();
});