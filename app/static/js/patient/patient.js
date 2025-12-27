console.log("✅ patient.js est chargé avec succès !");

// DEBUG: Afficher tous les rendez-vous et leurs statuts
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
async function refreshAppointments() {
    try {
        // Recharger la page pour récupérer les nouvelles données
        // OU faire un appel AJAX pour récupérer uniquement les RDV
        window.location.reload();
        
        // Alternative AJAX (si vous préférez ne pas recharger toute la page) :
        /*
        const response = await fetch('/patient/get_all_appointments_json');
        const data = await response.json();
        
        if (data.success) {
            appointments = data.appointments;
            renderAppointments();
            updateStats();
        }
        */
    } catch (error) {
        console.error('Erreur rafraîchissement:', error);
    }
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
            // Container pour les boutons
            const btnContainer = document.createElement('div');
            btnContainer.className = 'terminated-appointment-actions';
            btnContainer.style.cssText = 'display: flex; gap: 10px; margin-top: 12px; width: 100%;';
            // Bouton pour ouvrir le formulaire d'avis
            const btnOpenReview = document.createElement('button');
            btnOpenReview.className = 'patient-review-trigger';
            btnOpenReview.innerHTML = '⭐ Laisser un avis';
             btnOpenReview.style.flex = '1';
             // Bouton pour imprimer le reçu
            const btnPrint = document.createElement('button');
            btnPrint.className = 'btn-print-receipt';
            btnPrint.innerHTML = '<i class="fas fa-print"></i> Imprimer';
            btnPrint.style.cssText = 'flex: 1; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 10px 18px; border-radius: 10px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);';
            btnContainer.appendChild(btnOpenReview);
            btnContainer.appendChild(btnPrint);
            cardFooter.appendChild(btnContainer);
            // Event listener pour l'impression
            btnPrint.addEventListener('click', () => {
                printAppointmentReceipt(a);
            });
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

/**
 * Système de notifications - Affichage côté client
 */

// Charger le compteur au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('[NOTIF] Initialisation');
    loadNotificationCount();
    
    // Rafraîchir toutes les 30 secondes
    setInterval(loadNotificationCount, 30000);
});

/**
 * Charge le nombre de notifications non lues depuis le serveur
 */
function loadNotificationCount() {
    fetch('/patient/get_unread_count')
        .then(response => response.json())
        .then(data => {
            console.log('[NOTIF] Données reçues:', data);
            
            if (data.success && data.count > 0) {
                updateNotificationBadge(data.count);
            } else {
                hideNotificationBadge();
            }
        })
        .catch(error => {
            console.error('[NOTIF] ❌ Erreur:', error);
        });
}

/**
 * Affiche le badge avec le nombre de notifications
 */
function updateNotificationBadge(count) {
    const indicator = document.querySelector('.notification-indicator');
    
    if (indicator) {
        indicator.textContent = count;
        indicator.style.display = 'flex';
        console.log(`[NOTIF] ✅ Badge: ${count}`);
    }
}

/**
 * Cache le badge
 */
function hideNotificationBadge() {
    const indicator = document.querySelector('.notification-indicator');
    
    if (indicator) {
        indicator.style.display = 'none';
        console.log('[NOTIF] Badge caché');
    }
}

/**
 * Système de notifications complet
 */

// État du panneau (ouvert/fermé)
let panelOpen = false;

// Charger au démarrage
document.addEventListener('DOMContentLoaded', function() {
    console.log('[NOTIF] Initialisation');
    loadNotificationCount();
    
    // Rafraîchir toutes les 30 secondes
    setInterval(loadNotificationCount, 30000);
    
    // Événement clic sur la cloche
    const bell = document.querySelector('.notification-bell');
    if (bell) {
        bell.addEventListener('click', toggleNotificationPanel);
    }
    
    // Fermer le panneau si clic en dehors
    document.addEventListener('click', function(e) {
        const panel = document.getElementById('notificationPanel');
        const bell = document.querySelector('.notification-bell');
        
        if (panel && panelOpen && !panel.contains(e.target) && !bell.contains(e.target)) {
            closeNotificationPanel();
        }
    });
});

/**
 * Charge le nombre de notifications non lues
 */
function loadNotificationCount() {
    fetch('/patient/get_unread_count')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.count > 0) {
                updateNotificationBadge(data.count);
            } else {
                hideNotificationBadge();
            }
        })
        .catch(error => console.error('[NOTIF] Erreur:', error));
}

/**
 * Affiche le badge avec le nombre
 */
function updateNotificationBadge(count) {
    const indicator = document.querySelector('.notification-indicator');
    if (indicator) {
        indicator.textContent = count;
        indicator.style.display = 'flex';
    }
}

/**
 * Cache le badge
 */
function hideNotificationBadge() {
    const indicator = document.querySelector('.notification-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

/**
 * Ouvre/Ferme le panneau de notifications
 */
function toggleNotificationPanel() {
    if (panelOpen) {
        closeNotificationPanel();
    } else {
        openNotificationPanel();
    }
}

/**
 * Ouvre le panneau et charge les notifications
 */
function openNotificationPanel() {
    console.log('[NOTIF] Ouverture du panneau');
    
    // Créer le panneau s'il n'existe pas
    let panel = document.getElementById('notificationPanel');
    if (!panel) {
        panel = createNotificationPanel();
        document.body.appendChild(panel);
    }
    
    // Afficher le panneau
    panel.style.display = 'block';
    panelOpen = true;
    
    // Charger les notifications
    loadNotifications();
}

/**
 * Ferme le panneau
 */
function closeNotificationPanel() {
    const panel = document.getElementById('notificationPanel');
    if (panel) {
        panel.style.display = 'none';
        panelOpen = false;
    }
}

/**
 * Crée le panneau HTML
 */
function createNotificationPanel() {
    const panel = document.createElement('div');
    panel.id = 'notificationPanel';
    panel.className = 'notification-panel';
    panel.innerHTML = `
        <div class="notification-header">
            <h3>Notifications</h3>
            <button class="close-btn" onclick="closeNotificationPanel()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="notification-list" id="notificationList">
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i> Chargement...
            </div>
        </div>
    `;
    return panel;
}

/**
 * Charge les notifications depuis le serveur
 */
function loadNotifications() {
    const listContainer = document.getElementById('notificationList');
    
    fetch('/patient/get_notifications')
        .then(response => response.json())
        .then(data => {
            console.log('[NOTIF] Notifications reçues:', data);
            
            if (data.success && data.notifications.length > 0) {
                displayNotifications(data.notifications);
            } else {
                listContainer.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-bell-slash"></i>
                        <p>Aucune notification</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('[NOTIF] Erreur:', error);
            listContainer.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Erreur de chargement</p>
                </div>
            `;
        });
}

/**
 * Affiche les notifications dans le panneau
 */
function displayNotifications(notifications) {
    const listContainer = document.getElementById('notificationList');
    listContainer.innerHTML = '';
    
    notifications.forEach(notif => {
        const item = createNotificationItem(notif);
        listContainer.appendChild(item);
    });
}

/**
 * Crée un élément de notification
 */
function createNotificationItem(notif) {
    const item = document.createElement('div');
    item.className = `notification-item ${notif.lue ? 'read' : 'unread'}`;
    item.dataset.id = notif.id;
    
    const icon = getNotificationIcon(notif.type);
    const timeAgo = getTimeAgo(notif.date_creation);
    
    item.innerHTML = `
        <div class="notification-icon">
            <i class="${icon}"></i>
        </div>
        <div class="notification-content">
            <h4>${notif.titre}</h4>
            <p>${notif.message}</p>
            <span class="notification-time">${timeAgo}</span>
        </div>
        ${!notif.lue ? '<div class="unread-dot"></div>' : ''}
    `;
    
    // Clic pour marquer comme lu
    if (!notif.lue) {
        item.addEventListener('click', () => markAsRead(notif.id));
    }
    
    return item;
}

/**
 * Retourne l'icône selon le type de notification
 */
function getNotificationIcon(type) {
    const icons = {
        'rdv_confirme': 'fas fa-check-circle text-success',
        'rdv_annule': 'fas fa-times-circle text-danger',
        'rdv_refuse': 'fas fa-ban text-warning',
        'demande_avis': 'fas fa-star text-primary',
        'rappel_rdv': 'fas fa-bell text-info'
    };
    return icons[type] || 'fas fa-info-circle';
}

/**
 * Calcule le temps écoulé
 */
function getTimeAgo(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return "À l'instant";
    if (minutes < 60) return `Il y a ${minutes} min`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `Il y a ${hours}h`;
    
    const days = Math.floor(hours / 24);
    if (days < 7) return `Il y a ${days}j`;
    
    return date.toLocaleDateString('fr-FR');
}

/**
 * Marque une notification comme lue
 */
function markAsRead(notifId) {
    fetch(`/patient/mark_notification_read/${notifId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`[NOTIF] ✅ Notification ${notifId} marquée comme lue`);
            
            // Mettre à jour l'affichage
            const item = document.querySelector(`.notification-item[data-id="${notifId}"]`);
            if (item) {
                item.classList.remove('unread');
                item.classList.add('read');
                const dot = item.querySelector('.unread-dot');
                if (dot) dot.remove();
            }
            
            // Rafraîchir le compteur
            loadNotificationCount();
        }
    })
    .catch(error => console.error('[NOTIF] Erreur:', error));
}


//profile:

// ✅ DÉPLACER showMessage() EN DEHORS pour être accessible partout
function showMessage(message, type) {
    const flashMessage = document.getElementById('flashMessage');
    const icon = type === 'success' 
        ? '<i class="fas fa-check-circle"></i>' 
        : '<i class="fas fa-exclamation-circle"></i>';
    
    flashMessage.innerHTML = icon + '<span>' + message + '</span>';
    flashMessage.className = 'flash-message ' + (type === 'success' ? 'flash-success' : 'flash-error');
    flashMessage.style.display = 'flex';
    
    setTimeout(() => {
        flashMessage.style.opacity = '0';
        setTimeout(() => { 
            flashMessage.style.display = 'none'; 
            flashMessage.style.opacity = '1'; 
        }, 300);
    }, 3500);
}

// Fonction pour afficher/masquer le mot de passe
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = input.parentElement.querySelector('.password-toggle-btn i');
    
    if (input.type === 'password') {
        input.type = 'text';
        button.classList.remove('fa-eye');
        button.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        button.classList.remove('fa-eye-slash');
        button.classList.add('fa-eye');
    }
}

// Réinitialiser le formulaire
function resetPasswordChangeForm() {
    const form = document.getElementById('passwordChangeForm');
    form.reset();
    
    const passwordInputs = form.querySelectorAll('input[type="text"]');
    passwordInputs.forEach(input => {
        if (input.id.includes('pwd_')) {
            input.type = 'password';
            const icon = input.parentElement.querySelector('.password-toggle-btn i');
            if (icon) {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }
    });
    
    form.querySelectorAll('.password-form-input').forEach(input => {
        input.classList.remove('is-valid', 'is-invalid');
    });
}
 // ========================================
    // 1️⃣ GESTION DU PROFIL
    // ========================================
document.addEventListener('DOMContentLoaded', function () {
    // ========================================
    // 1️⃣ GESTION DU PROFIL (uniquement si sur la page profil)
    // ========================================
    const form = document.getElementById('personalInfoForm');
    
    // ✅ Vérifier que le formulaire existe avant de continuer
    if (form) {
        const btnEdit = document.getElementById('btnEdit');
        const btnCancel = document.getElementById('btnCancel');
        const actions = document.getElementById('personalInfoActions');
        const inputs = form.querySelectorAll('input');

        let originalValues = {};
        inputs.forEach(input => {
            originalValues[input.name] = input.value;
        });

        btnEdit.addEventListener('click', function() {
            inputs.forEach(input => input.removeAttribute('readonly'));
            inputs[0].focus();
            actions.style.display = 'flex';
            btnEdit.style.display = 'none';
        });

        btnCancel.addEventListener('click', function() {
            inputs.forEach(input => {
                input.value = originalValues[input.name];
                input.setAttribute('readonly', true);
            });
            actions.style.display = 'none';
            btnEdit.style.display = 'flex';
        });

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const nom = form.querySelector('#nom').value.trim();
            const email = form.querySelector('#email').value.trim();
            const telephone = form.querySelector('#telephone').value.trim();

            if (!nom || !email || !telephone) {
                showMessage("Tous les champs sont requis.", 'error');
                return;
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showMessage("Veuillez entrer une adresse email valide.", 'error');
                return;
            }

            const phoneRegex = /^[0-9]{10}$/;
            if (!phoneRegex.test(telephone)) {
                showMessage("Le numéro de téléphone doit contenir exactement 10 chiffres.", 'error');
                return;
            }

            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, 'success');
                    
                    inputs.forEach(input => {
                        originalValues[input.name] = input.value;
                        input.setAttribute('readonly', true);
                    });
                    
                    actions.style.display = 'none';
                    btnEdit.style.display = 'flex';
                    
                    document.querySelector('.profile-hero-name').textContent = nom;
                    document.querySelector('.profile-hero-email').innerHTML = 
                        '<i class="fas fa-envelope"></i>' + email;
                    document.querySelector('.avatar-circle').textContent = nom[0].toUpperCase();
                } else {
                    showMessage(data.message || "Erreur lors de la mise à jour.", 'error');
                }
            })
            .catch(err => {
                console.error(err);
                showMessage("Erreur de connexion au serveur.", 'error');
            });
        });
    } // ✅ Fin du if (form)

    // ========================================
    // 2️⃣ GESTION DU CHANGEMENT DE MOT DE PASSE (uniquement si sur la page profil)
    // ========================================
    const passwordForm = document.getElementById('passwordChangeForm');
    
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const currentPassword = document.getElementById('pwd_current_password').value.trim();
            const newPassword = document.getElementById('pwd_new_password').value.trim();
            const confirmPassword = document.getElementById('pwd_confirm_password').value.trim();
            
            if (!currentPassword || !newPassword || !confirmPassword) {
                showMessage("Tous les champs sont requis.", 'error');
                return;
            }
            
            if (newPassword.length < 8) {
                showMessage("Le nouveau mot de passe doit contenir au moins 8 caractères.", 'error');
                document.getElementById('pwd_new_password').classList.add('is-invalid');
                return;
            }
            
            if (newPassword !== confirmPassword) {
                showMessage("Les nouveaux mots de passe ne correspondent pas.", 'error');
                document.getElementById('pwd_confirm_password').classList.add('is-invalid');
                return;
            }
            
            if (newPassword === currentPassword) {
                showMessage("Le nouveau mot de passe doit être différent de l'ancien.", 'error');
                return;
            }
            
            const submitBtn = passwordForm.querySelector('.password-btn-save');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Traitement...';
            
            const formData = new FormData(passwordForm);
            
            fetch('/patient/change_password', {  // ✅ URL en dur au lieu de {{ url_for }}
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message || 'Mot de passe modifié avec succès', 'success');
                    resetPasswordChangeForm();
                } else {
                    showMessage(data.message || "Erreur lors du changement de mot de passe.", 'error');
                }
            })
            .catch(err => {
                console.error(err);
                showMessage("Erreur de connexion au serveur.", 'error');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
        
        // Validation en temps réel
        const newPasswordInput = document.getElementById('pwd_new_password');
        const confirmPasswordInput = document.getElementById('pwd_confirm_password');
        
        if (newPasswordInput) {
            newPasswordInput.addEventListener('input', function() {
                if (this.value.length >= 8) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
                
                if (confirmPasswordInput && confirmPasswordInput.value) {
                    if (this.value === confirmPasswordInput.value) {
                        confirmPasswordInput.classList.remove('is-invalid');
                        confirmPasswordInput.classList.add('is-valid');
                    } else {
                        confirmPasswordInput.classList.remove('is-valid');
                        confirmPasswordInput.classList.add('is-invalid');
                    }
                }
            });
        }
        
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', function() {
                if (newPasswordInput && this.value === newPasswordInput.value && this.value.length >= 8) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        }
    } // ✅ Fin du if (passwordForm)
});
/**
 * Charge le prochain rendez-vous pour le badge
 */
function loadNextAppointment() {
    fetch('/patient/get_next_appointment')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('nextRdvBadge');
            
            if (!badge) return;
            
            if (data.success && data.appointment) {
                // Mettre à jour le badge avec les vraies données
                badge.innerHTML = `
                    <i class="fas fa-calendar-day"></i>
                    <div class="rdv-info">
                        <small>Prochain RDV</small>
                        <strong>${data.appointment.date}</strong>
                    </div>
                `;
                
                // Ajouter un tooltip au survol
                badge.title = `${data.appointment.medecin} à ${data.appointment.time}`;
                
                console.log('[NEXT-RDV] ✅ Chargé:', data.appointment);
            } else {
                // Aucun RDV à venir
                badge.innerHTML = `
                    <i class="fas fa-calendar-day"></i>
                    <div class="rdv-info">
                        <small>Prochain RDV</small>
                        <strong>Aucun</strong>
                    </div>
                `;
                badge.style.opacity = '0.6';
                
                console.log('[NEXT-RDV] ⚠️ Aucun RDV');
            }
        })
        .catch(error => {
            console.error('[NEXT-RDV] ❌ Erreur:', error);
            
            // En cas d'erreur, afficher "Indisponible"
            const badge = document.getElementById('nextRdvBadge');
            if (badge) {
                badge.innerHTML = `
                    <i class="fas fa-calendar-day"></i>
                    <div class="rdv-info">
                        <small>Prochain RDV</small>
                        <strong>--</strong>
                    </div>
                `;
            }
        });
}

// Charger au démarrage de la page
document.addEventListener('DOMContentLoaded', function() {
    loadNextAppointment();
    
    // Optionnel: Rafraîchir toutes les 5 minutes
     setInterval(loadNextAppointment, 5 * 60 * 1000);
});







//add facture
/**
 * Affiche la facture d'un rendez-vous
 */
function printAppointmentReceipt(appointment) {
    console.log('🧾 Chargement facture pour RDV:', appointment.id);
    
    // Afficher un loader
    showToast("📄 Génération de la facture...", false);
    
    fetch(`/patient/get_invoice/${appointment.id}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayInvoiceModal(data.invoice);
            } else {
                showToast("❌ " + (data.message || "Erreur"), true);
            }
        })
        .catch(err => {
            console.error('Erreur:', err);
            showToast("❌ Erreur de chargement", true);
        });
}

/**
 * Affiche le modal de facture
 */
function displayInvoiceModal(invoice) {
    const modalHTML = `
        <div class="invoice-overlay" id="invoiceOverlay">
            <div class="invoice-modal">
                <div class="invoice-header">
                    <div class="invoice-logo">
                        <h1>WeCare</h1>
                        <p>Plateforme Médicale</p>
                    </div>
                    <div class="invoice-title">
                        <h2>FACTURE</h2>
                        <p>N° ${invoice.invoice_number}</p>
                        <p>Date: ${invoice.date_emission}</p>
                    </div>
                </div>
                
                <div class="invoice-body">
                    <div class="invoice-parties">
                        <div class="invoice-party">
                            <h3>Patient</h3>
                            <p><strong>${invoice.patient.nom}</strong></p>
                            <p>${invoice.patient.email}</p>
                            <p>${invoice.patient.telephone}</p>
                        </div>
                        <div class="invoice-party">
                            <h3>Médecin</h3>
                            <p><strong>Dr. ${invoice.medecin.nom}</strong></p>
                            <p>${invoice.medecin.specialite}</p>
                            <p>${invoice.medecin.adresse || ''}</p>
                            <p>${invoice.medecin.telephone}</p>
                        </div>
                    </div>
                    
                    <div class="invoice-details">
                        <h3>Détails de la consultation</h3>
                        <table class="invoice-table">
                            <thead>
                                <tr>
                                    <th>Description</th>
                                    <th>Date</th>
                                    <th>Montant HT</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>${invoice.consultation.motif}</td>
                                    <td>${invoice.consultation.date}</td>
                                    <td>${invoice.montants.tarif_ht} MAD</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="invoice-totals">
                        <div class="total-line">
                            <span>Sous-total HT:</span>
                            <strong>${invoice.montants.tarif_ht} MAD</strong>
                        </div>
                        <div class="total-line">
                            <span>TVA (${invoice.montants.tva_rate}%):</span>
                            <strong>${invoice.montants.tva_amount} MAD</strong>
                        </div>
                        <div class="total-line total-final">
                            <span>Total TTC:</span>
                            <strong>${invoice.montants.total_ttc} MAD</strong>
                        </div>
                    </div>
                </div>
                
                <div class="invoice-footer">
                    <button class="btn-download" onclick="downloadInvoicePDF()">
                        <i class="fas fa-download"></i> Télécharger PDF
                    </button>
                    <button class="btn-close-invoice" onclick="closeInvoiceModal()">
                        <i class="fas fa-times"></i> Fermer
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    document.body.style.overflow = 'hidden';
}

/**
 * Ferme le modal de facture
 */
function closeInvoiceModal() {
    const modal = document.getElementById('invoiceOverlay');
    if (modal) {
        modal.remove();
        document.body.style.overflow = 'auto';
    }
}



/**
 * Télécharge la facture en PDF - VERSION IMPRESSION AMÉLIORÉE
 */
function downloadInvoicePDF() {
    showToast("📄 Préparation de l'impression...", false);
    
    const invoiceModal = document.querySelector('.invoice-modal');
    const invoiceFooter = document.querySelector('.invoice-footer');
    
    if (!invoiceModal) {
        showToast("❌ Erreur: Modal introuvable", true);
        return;
    }
    
    // Créer une nouvelle fenêtre pour l'impression
    const printWindow = window.open('', '_blank', 'width=800,height=600');
    
    // Cloner le contenu
    const content = invoiceModal.cloneNode(true);
    
    // Retirer le footer du clone
    const footerClone = content.querySelector('.invoice-footer');
    if (footerClone) {
        footerClone.remove();
    }
    
    // Écrire le HTML avec tous les styles
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Facture WeCare</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" />
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: Arial, sans-serif;
                    background: white;
                    padding: 20px;
                }
                
                .invoice-modal {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    box-shadow: none;
                    border-radius: 0;
                }
                
                .invoice-header {
                    display: flex;
                    justify-content: space-between;
                    padding: 30px;
                    border-bottom: 3px solid #667eea;
                    background: linear-gradient(135deg, #f6f8fb 0%, #eef2f7 100%);
                }
                
                .invoice-logo h1 {
                    color: #667eea;
                    margin: 0;
                    font-size: 28px;
                }
                
                .invoice-logo p {
                    color: #718096;
                    margin: 5px 0 0 0;
                    font-size: 14px;
                }
                
                .invoice-title {
                    text-align: right;
                }
                
                .invoice-title h2 {
                    margin: 0 0 10px 0;
                    color: #1a202c;
                }
                
                .invoice-title p {
                    margin: 5px 0;
                    color: #718096;
                    font-size: 14px;
                }
                
                .invoice-body {
                    padding: 30px;
                }
                
                .invoice-parties {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                    margin-bottom: 30px;
                }
                
                .invoice-party h3 {
                    color: #667eea;
                    margin-bottom: 10px;
                    border-bottom: 2px solid #eef2f7;
                    padding-bottom: 8px;
                    font-size: 16px;
                }
                
                .invoice-party p {
                    margin: 8px 0;
                    color: #2d3748;
                    font-size: 14px;
                }
                
                .invoice-details h3 {
                    color: #1a202c;
                    margin-bottom: 15px;
                    font-size: 18px;
                }
                
                .invoice-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }
                
                .invoice-table th,
                .invoice-table td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e2e8f0;
                }
                
                .invoice-table th {
                    background: #f6f8fb;
                    font-weight: 600;
                    color: #2d3748;
                }
                
                .invoice-totals {
                    margin-top: 30px;
                    padding: 20px;
                    background: #f6f8fb;
                    border-radius: 8px;
                }
                
                .total-line {
                    display: flex;
                    justify-content: space-between;
                    padding: 10px 0;
                }
                
                .total-final {
                    border-top: 2px solid #667eea;
                    margin-top: 10px;
                    padding-top: 15px;
                    font-size: 18px;
                    color: #667eea;
                    font-weight: bold;
                }
                
                @media print {
                    body {
                        padding: 0;
                    }
                    
                    .invoice-modal {
                        box-shadow: none;
                    }
                    
                    /* Forcer les couleurs à l'impression */
                    .invoice-header {
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                        background: #f6f8fb !important;
                    }
                    
                    .invoice-party h3 {
                        color: #667eea !important;
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }
                    
                    .total-final {
                        color: #667eea !important;
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }
                    
                    .invoice-table th {
                        background: #f6f8fb !important;
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }
                    
                    .invoice-totals {
                        background: #f6f8fb !important;
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }
                }
            </style>
        </head>
        <body>
            ${content.outerHTML}
            <script>
                window.onload = function() {
                    window.print();
                };
                
                window.onafterprint = function() {
                    window.close();
                };
            </script>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    
    showToast("✅ Fenêtre d'impression ouverte!", false);
}