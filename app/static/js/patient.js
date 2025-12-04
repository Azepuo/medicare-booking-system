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
    specSelect.addEventListener('change', function () {
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
    doctorSelect.addEventListener('change', function () {
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
    dateSelect.addEventListener('change', function () {
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
    document.getElementById('editAppointmentForm').addEventListener('submit', function (e) {
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
// Render cards - VERSION COMPLÈTEMENT REFAITE AVEC ANIMATIONS FIXES
// Render cards - VERSION COMPLÈTEMENT REFAITE AVEC ANIMATIONS FIXES
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

    // Filtrage avec statuts normalisés
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

        const showModifier = !(a.normalizedStatus === 'terminé' || a.normalizedStatus === 'annulé');
        const showAnnuler = (a.normalizedStatus === 'En attente' || a.normalizedStatus === 'confirmé');

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

        // ⭐ Ajout du système d'avis pour les rendez-vous terminés
        if (a.normalizedStatus === 'terminé') {
            const cardFooter = card.querySelector('.card-footer');
            
            // Bouton pour ouvrir le formulaire d'avis
            const btnOpenReview = document.createElement('button');
            btnOpenReview.className = 'patient-review-trigger';
            btnOpenReview.innerHTML = '⭐ Laisser un avis';
            
            cardFooter.appendChild(btnOpenReview);
            
            // Vérifier si un avis existe déjà pour ce RDV
            btnOpenReview.addEventListener('click', () => {
                // D'abord vérifier si un avis existe
                fetch(`/patient/get_appointment_review/${a.id}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.success && data.has_review) {
                            // Avis existe déjà - ouvrir en mode modification
                            openReviewModalForAppointment(a, data.review);
                        } else {
                            // Pas d'avis - ouvrir en mode création
                            openReviewModalForAppointment(a, null);
                        }
                    })
                    .catch(err => {
                        console.error('Erreur:', err);
                        // En cas d'erreur, ouvrir quand même le modal
                        openReviewModalForAppointment(a, null);
                    });
            });
        }

        grid.appendChild(card);
    });
}

// 🎯 Ouvrir le modal d'avis (créé dynamiquement)
function openReviewModalForAppointment(appointment, existingReview = null) {
    // Déterminer le mode (création ou modification)
    const isEditing = existingReview !== null;
    const modalTitle = isEditing ? 'Modifier votre avis' : 'Évaluez votre consultation';
    const submitBtnText = isEditing ? 'Mettre à jour l\'avis' : 'Ajouter l\'avis';
    
    console.log('📝 Ouverture modal:', isEditing ? 'MODE MODIFICATION' : 'MODE CRÉATION');
    if (isEditing) {
        console.log('Avis existant:', existingReview);
    }
    
    // Créer le modal à chaque fois (évite les conflits)
    const modalContainer = document.createElement('div');
    modalContainer.className = 'patient-feedback-overlay';
    modalContainer.id = `review-modal-${appointment.id}`;
    
    modalContainer.innerHTML = `
        <div class="patient-feedback-backdrop"></div>
        <div class="patient-feedback-card">
            <div class="patient-feedback-header">
                <h3>${modalTitle}</h3>
                <button class="patient-feedback-close-x">&times;</button>
            </div>
            <div class="patient-feedback-body">
                ${isEditing ? '<div class="patient-edit-notice">✏️ Vous modifiez votre avis précédent</div>' : ''}
                
                <div class="patient-doctor-info-box">
                    <strong>${appointment.medecin_name}</strong>
                    <span>${appointment.medecin_spec}</span>
                </div>
                
                <div class="patient-stars-section">
                    <label>Note globale</label>
                    <div class="patient-stars-container" data-rating="${existingReview ? existingReview.note : 0}">
                        <span class="patient-star-icon" data-star-val="1">★</span>
                        <span class="patient-star-icon" data-star-val="2">★</span>
                        <span class="patient-star-icon" data-star-val="3">★</span>
                        <span class="patient-star-icon" data-star-val="4">★</span>
                        <span class="patient-star-icon" data-star-val="5">★</span>
                    </div>
                </div>
                
                <div class="patient-textarea-section">
                    <label>Votre commentaire</label>
                    <textarea 
                        class="patient-comment-textarea" 
                        placeholder="Partagez votre expérience avec ce médecin (minimum 10 caractères)..."
                        rows="4"
                        maxlength="500"
                    >${existingReview ? existingReview.commentaire : ''}</textarea>
                    <div class="patient-char-limit">
                        <span class="patient-char-num">${existingReview ? existingReview.commentaire.length : 0}</span>/500
                        <span class="patient-char-hint">• Minimum 10 caractères requis</span>
                    </div>
                </div>
                
                <button class="patient-publish-btn">${submitBtnText}</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modalContainer);
    
    // Forcer le reflow avant d'ajouter la classe active
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            modalContainer.classList.add('feedback-modal-visible');
        });
    });
    
    document.body.style.overflow = 'hidden';
    
    // Configurer les événements du modal
    setupReviewModalEvents(modalContainer, appointment.id, existingReview);
}

// 🎯 Configurer les événements du modal
function setupReviewModalEvents(modalElement, appointmentId, existingReview = null) {
    const closeBtn = modalElement.querySelector('.patient-feedback-close-x');
    const backdrop = modalElement.querySelector('.patient-feedback-backdrop');
    const starIcons = modalElement.querySelectorAll('.patient-star-icon');
    const starsContainer = modalElement.querySelector('.patient-stars-container');
    const commentTextarea = modalElement.querySelector('.patient-comment-textarea');
    const charNum = modalElement.querySelector('.patient-char-num');
    const publishBtn = modalElement.querySelector('.patient-publish-btn');
    
    // Initialiser les étoiles si on est en mode modification
    if (existingReview && existingReview.note) {
        updateStarsVisual(starIcons, existingReview.note);
        console.log('⭐ Étoiles initialisées:', existingReview.note);
    }
    
    // Fonction pour fermer le modal
    const closeModalWithAnimation = () => {
        modalElement.classList.remove('feedback-modal-visible');
        setTimeout(() => {
            modalElement.remove();
            document.body.style.overflow = 'auto';
        }, 350);
    };
    
    // Bouton fermer
    closeBtn.addEventListener('click', closeModalWithAnimation);
    backdrop.addEventListener('click', closeModalWithAnimation);
    
    // Gestion des étoiles - Click
    starIcons.forEach(star => {
        star.addEventListener('click', () => {
            const rating = parseInt(star.dataset.starVal);
            starsContainer.dataset.rating = rating;
            updateStarsVisual(starIcons, rating);
        });
        
        // Hover effect
        star.addEventListener('mouseenter', () => {
            const hoverVal = parseInt(star.dataset.starVal);
            starIcons.forEach((s, i) => {
                if (i < hoverVal) {
                    s.classList.add('patient-star-hovered');
                } else {
                    s.classList.remove('patient-star-hovered');
                }
            });
        });
    });
    
    // Reset hover
    starsContainer.addEventListener('mouseleave', () => {
        starIcons.forEach(s => s.classList.remove('patient-star-hovered'));
    });
    
    // Compteur de caractères avec validation visuelle
    commentTextarea.addEventListener('input', () => {
        const length = commentTextarea.value.length;
        charNum.textContent = length;
        
        // Changer la couleur selon la validation
        const charLimit = commentTextarea.parentElement.querySelector('.patient-char-limit');
        if (length < 10) {
            charLimit.style.color = '#ef4444'; // Rouge si < 10
            charNum.style.fontWeight = '700';
        } else if (length >= 10 && length <= 500) {
            charLimit.style.color = '#10b981'; // Vert si valide
            charNum.style.fontWeight = '700';
        } else {
            charLimit.style.color = '#ef4444'; // Rouge si > 500
            charNum.style.fontWeight = '700';
        }
    });
    
    // Publier l'avis
    publishBtn.addEventListener('click', () => {
        const rating = parseInt(starsContainer.dataset.rating);
        const comment = commentTextarea.value.trim();
        
        // Validation de la note
        if (rating === 0) {
            displayUserAlert('⚠️ Veuillez sélectionner une note', 'warning');
            return;
        }
        
        // Validation du commentaire - vide
        if (!comment) {
            displayUserAlert('⚠️ Veuillez ajouter un commentaire', 'warning');
            return;
        }
        
        // Validation du commentaire - minimum 10 caractères
        if (comment.length < 10) {
            displayUserAlert('⚠️ Le commentaire doit contenir au moins 10 caractères', 'warning');
            return;
        }
        
        // Validation du commentaire - maximum 500 caractères
        if (comment.length > 500) {
            displayUserAlert('⚠️ Le commentaire ne peut pas dépasser 500 caractères', 'warning');
            return;
        }
        
        // Envoyer au backend
        sendReviewToBackend(appointmentId, rating, comment);
        closeModalWithAnimation();
    });
}

// 🎨 Mettre à jour l'affichage des étoiles
function updateStarsVisual(starElements, rating) {
    starElements.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('patient-star-selected');
        } else {
            star.classList.remove('patient-star-selected');
        }
    });
}

// 📤 Envoyer l'avis au backend
async function sendReviewToBackend(appointmentId, rating, comment) {
    try {
        const response = await fetch('/patient/submit_review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                appointment_id: appointmentId,
                rating: rating,
                comment: comment
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayUserAlert('✅ Votre avis a été Enregistrer avec succès!', 'success');
            console.log('Avis publié:', data);
        } else {
            displayUserAlert('❌ Erreur lors de la publication', 'danger');
        }
    } catch (error) {
        console.error('Erreur:', error);
        displayUserAlert('❌ Erreur de connexion', 'danger');
    }
}

// 🔔 Afficher une alerte utilisateur
function displayUserAlert(message, alertType) {
    const alertBox = document.createElement('div');
    alertBox.className = `patient-alert-box patient-alert-${alertType}`;
    alertBox.textContent = message;
    document.body.appendChild(alertBox);
    
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            alertBox.classList.add('patient-alert-shown');
        });
    });
    
    setTimeout(() => {
        alertBox.classList.remove('patient-alert-shown');
        setTimeout(() => alertBox.remove(), 350);
    }, 3500);
}

// CSS - VERSION COMPLÈTE REFAITE
const patientReviewStyles = `
/* Bouton trigger */
.patient-review-trigger {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.3s ease;
    margin-top: 12px;
    width: 100%;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.patient-review-trigger:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
}

.patient-review-trigger:active {
    transform: translateY(0);
}

/* Overlay Modal Container */
.patient-feedback-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 99999;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease, visibility 0.3s ease;
}

.patient-feedback-overlay.feedback-modal-visible {
    opacity: 1;
    visibility: visible;
}

/* Backdrop */
.patient-feedback-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(5px);
}

/* Modal Card */
.patient-feedback-card {
    position: relative;
    background: #ffffff;
    border-radius: 20px;
    width: 90%;
    max-width: 520px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 25px 70px rgba(0, 0, 0, 0.4);
    transform: scale(0.8) translateY(40px);
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.patient-feedback-overlay.feedback-modal-visible .patient-feedback-card {
    transform: scale(1) translateY(0);
    opacity: 1;
}

/* Header */
.patient-feedback-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 28px;
    border-bottom: 2px solid #f0f1f3;
}

.patient-feedback-header h3 {
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    color: #1a202c;
}

.patient-feedback-close-x {
    background: transparent;
    border: none;
    font-size: 32px;
    color: #718096;
    cursor: pointer;
    line-height: 1;
    padding: 0;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    transition: all 0.2s ease;
}

.patient-feedback-close-x:hover {
    background: #edf2f7;
    color: #2d3748;
    transform: rotate(90deg);
}

/* Body */
.patient-feedback-body {
    padding: 28px;
}

/* Edit Notice */
.patient-edit-notice {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    color: #92400e;
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 20px;
    font-size: 14px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    border-left: 4px solid #f59e0b;
}

/* Doctor Info Box */
.patient-doctor-info-box {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 18px;
    background: linear-gradient(135deg, #f6f8fb 0%, #eef2f7 100%);
    border-radius: 14px;
    margin-bottom: 28px;
    border-left: 4px solid #667eea;
}

.patient-doctor-info-box strong {
    font-size: 17px;
    color: #1a202c;
    font-weight: 600;
}

.patient-doctor-info-box span {
    font-size: 14px;
    color: #718096;
}

/* Stars Section */
.patient-stars-section {
    margin-bottom: 28px;
}

.patient-stars-section label {
    display: block;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 14px;
    font-size: 15px;
}

.patient-stars-container {
    display: flex;
    gap: 10px;
    font-size: 42px;
}

.patient-star-icon {
    cursor: pointer;
    color: #cbd5e0;
    transition: all 0.25s ease;
    user-select: none;
}

.patient-star-icon:hover,
.patient-star-icon.patient-star-hovered {
    color: #fbbf24;
    transform: scale(1.15) rotate(-5deg);
}

.patient-star-icon.patient-star-selected {
    color: #f59e0b;
    animation: starPulse 0.4s ease;
}

@keyframes starPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.2); }
}

/* Textarea Section */
.patient-textarea-section {
    margin-bottom: 28px;
}

.patient-textarea-section label {
    display: block;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 10px;
    font-size: 15px;
}

.patient-comment-textarea {
    width: 100%;
    padding: 14px;
    border: 2px solid #e2e8f0;
    border-radius: 14px;
    font-size: 15px;
    font-family: inherit;
    resize: vertical;
    transition: all 0.25s ease;
    line-height: 1.6;
}

.patient-comment-textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
}

.patient-char-limit {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    color: #718096;
    margin-top: 6px;
    font-weight: 500;
}

.patient-char-hint {
    font-size: 12px;
    color: #a0aec0;
    font-weight: 400;
}

/* Publish Button */
.patient-publish-btn {
    width: 100%;
    padding: 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 14px;
    font-size: 17px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.patient-publish-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
}

.patient-publish-btn:active {
    transform: translateY(-1px);
}

/* Alert Box */
.patient-alert-box {
    position: fixed;
    top: 24px;
    right: 24px;
    padding: 18px 26px;
    border-radius: 14px;
    font-weight: 600;
    font-size: 15px;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.25);
    z-index: 999999;
    transform: translateX(450px);
    opacity: 0;
    transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.patient-alert-box.patient-alert-shown {
    transform: translateX(0);
    opacity: 1;
}

.patient-alert-box.patient-alert-success {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
}

.patient-alert-box.patient-alert-danger {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
}

.patient-alert-box.patient-alert-warning {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
}

/* Scrollbar personnalisée */
.patient-feedback-card::-webkit-scrollbar {
    width: 8px;
}

.patient-feedback-card::-webkit-scrollbar-track {
    background: #f1f3f5;
    border-radius: 10px;
}

.patient-feedback-card::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 10px;
}

.patient-feedback-card::-webkit-scrollbar-thumb:hover {
    background: #a0aec0;
}

/* Responsive */
@media (max-width: 640px) {
    .patient-feedback-card {
        width: 96%;
        margin: 10px;
    }
    
    .patient-stars-container {
        font-size: 36px;
        gap: 8px;
    }
    
    .patient-feedback-header h3 {
        font-size: 19px;
    }
    
    .patient-alert-box {
        right: 12px;
        left: 12px;
        top: 12px;
    }
}
`;

// Injecter les styles une seule fois
if (!document.getElementById('patient-review-unique-styles')) {
    const styleTag = document.createElement('style');
    styleTag.id = 'patient-review-unique-styles';
    styleTag.textContent = patientReviewStyles;
    document.head.appendChild(styleTag);
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
document.addEventListener('DOMContentLoaded', function () {
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
        link.addEventListener('click', function (e) {
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