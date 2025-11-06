  
    const appointments = [
      {id: 1, date: "2025-11-08", time: "09:00", medecin_name: "Doctor1", medecin_spec: "specialite1", status: "terminé", clinic: "Adresse1"},
      {id: 2, date: "2025-11-10", time: "15:00", medecin_name: "Doctor2", medecin_spec: "specialite2", status: "confirmé", clinic: "Adresse2"},
      {id: 3, date: "2025-12-02", time: "11:30", medecin_name: "Doctor3", medecin_spec: "specialite3", status: "annulé", clinic: "Adresse3"},
      {id: 4, date: "2025-10-25", time: "16:00", medecin_name: "Doctor4", medecin_spec: "specialite4", status: "terminé", clinic: "Adresse4"},
      {id: 5, date: "2025-11-15", time: "10:30", medecin_name: "Doctor5", medecin_spec: "specialite5", status: "confirmé", clinic: "Adresse5"},
      {id: 6, date: "2025-09-20", time: "14:00", medecin_name: "Doctor6", medecin_spec: "specialite6", status: "terminé",  clinic: "Adresse6"},
      {id: 6, date: "2025-09-20", time: "14:00", medecin_name: "Doctor7", medecin_spec: "specialite7", status: "terminé",  clinic: "Adresse7"}
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
      const total = appointments.length;
      const confirmed = appointments.filter(a => a.status === 'confirmé').length;
      const done = appointments.filter(a => a.status === 'terminé').length;
      const cancelled = appointments.filter(a => a.status === 'annulé').length;

      document.getElementById('stats').innerHTML = `
        <div class="stat-card">
          <div class="stat-icon total">📊</div>
          <div class="stat-info">
            <h3>Total</h3>
            <p>${total}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon confirmed">✅</div>
          <div class="stat-info">
            <h3>Confirmés</h3>
            <p>${confirmed}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon done">✔️</div>
          <div class="stat-info">
            <h3>Terminés</h3>
            <p>${done}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon cancelled">❌</div>
          <div class="stat-info">
            <h3>Annulés</h3>
            <p>${cancelled}</p>
          </div>
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
              <button class="btn btn-primary" onclick="viewDetails(${apt.id})">Détails</button>
            </div>
          </div>
        </div>
      `).join('');
    }

    function viewDetails(id) {
      const apt = appointments.find(a => a.id === id);
      alert(`Détails du rendez-vous:\n\nMédecin: ${apt.medecin_name}\nSpécialité: ${apt.medecin_spec}\nDate: ${formatDate(apt.date)}\nHeure: ${apt.time}\nStatut: ${apt.status}\nClinique: ${apt.clinic}`);
    }

    function cancelAppointment(id) {
      if (confirm('Êtes-vous sûr de vouloir annuler ce rendez-vous ?')) {
        const apt = appointments.find(a => a.id === id);
        apt.status = 'annulé';
        updateStats();
        renderAppointments();
      }
    }

    document.getElementById('searchInput').addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase();
      renderAppointments();
    });

    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderAppointments();
      });
    });

    updateStats();
    renderAppointments();
  