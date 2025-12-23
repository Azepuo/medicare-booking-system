// medecin.js - main frontend logic for Medecin section
(async () => {
  // Base URL du gateway HTTP -> adapte-le
  const API_BASE = '/api/medecin'; // ex: http://localhost:5000/api/medecin

  // Small helpers
  const $ = sel => document.querySelector(sel);
  const $$ = sel => Array.from(document.querySelectorAll(sel));
  const notify = (msg, type='info') => {
    // simple notification: you can expand
    const n = document.createElement('div');
    n.textContent = msg; n.style.position='fixed'; n.style.right='18px'; n.style.bottom='18px';
    n.style.padding='10px 14px'; n.style.borderRadius='10px'; n.style.boxShadow='0 6px 20px rgba(13,46,77,0.08)';
    n.style.background = (type==='error')? '#ffefef' : '#eaf4ff'; n.style.color='#0b2545';
    document.body.appendChild(n);
    setTimeout(()=>n.remove(), 3500);
  };

  // fetch wrapper
  async function api(path, opts={}){
    try{
      const res = await fetch(API_BASE + path, Object.assign({
        headers:{'Content-Type':'application/json'},
        credentials: 'include'
      }, opts));
      if(!res.ok){
        const txt = await res.text().catch(()=>null);
        throw new Error(res.status + ' ' + (txt || res.statusText));
      }
      return await res.json().catch(()=>null);
    } catch(err){
      console.error('API error', err);
      notify('Erreur API: '+err.message, 'error');
      throw err;
    }
  }

  // Load basic profile displayed in the topbar
  async function loadProfile(){
    try{
      const data = await api('/profil'); // GET /profil
      if(!data) return;
      $('#medecinName').textContent = data.nom || 'Dr. —';
      // avatar if present
      if(data.avatar) {
        document.querySelector('.profile img').src = data.avatar;
      }
    } catch(e){ console.warn('profil non chargé', e) }
  }

  // Page: dashboard
  async function page_dashboard(){
    // summary cards
    const stats = await api('/statistiques/summary'); // { total_rdv, rdv_today, taux_annulation, revenus }
    const container = document.getElementById('page-content');
    container.innerHTML = `
      <div class="header-row">
        <h2 class="h1">Tableau de bord</h2>
        <div><button class="btn" id="refreshDash">Rafraîchir</button></div>
      </div>
      <div class="grid">
        <div class="card"><h3>Rendez-vous totaux</h3><p id="card-total">--</p></div>
        <div class="card"><h3>RDV aujourd'hui</h3><p id="card-today">--</p></div>
        <div class="card"><h3>Taux d'annulation</h3><p id="card-cancel">--</p></div>
      </div>
      <div style="margin-top:12px" class="card">
        <canvas id="chart-rdv" height="120"></canvas>
      </div>
    `;
    $('#refreshDash').addEventListener('click', page_dashboard);

    // populate
    if(stats){
      $('#card-total').textContent = stats.total_rdv ?? '0';
      $('#card-today').textContent = stats.rdv_today ?? '0';
      $('#card-cancel').textContent = (stats.taux_annulation ? (stats.taux_annulation + '%') : '0%');
      // chart
      const ctx = document.getElementById('chart-rdv').getContext('2d');
      new Chart(ctx, {
        type:'line',
        data:{
          labels: stats.last_days?.map(x=>x.day) || ['J-6','J-5','J-4','J-3','J-2','J-1','Aujourd\'hui'],
          datasets:[{label:'RDV',data: stats.last_days?.map(x=>x.count)||[0,1,2,1,4,3,5], tension:0.35}]
        },
        options:{plugins:{legend:{display:false}}}
      });
    }
  }

  // Page: rdv du jour
  async function page_rdv_du_jour(){
    const rdvs = await api('/rdv/today'); // returns array
    const container = document.getElementById('page-content');
    container.innerHTML = `
      <div class="header-row"><h2 class="h1">Rendez-vous du jour</h2></div>
      <div class="card">
        <table class="table" id="rdvTable">
          <thead><tr><th>Heure</th><th>Patient</th><th>Motif</th><th>Statut</th><th>Actions</th></tr></thead>
          <tbody>${(rdvs || []).map(r=>`<tr data-id="${r.id}">
            <td>${r.heure}</td>
            <td>${r.patient_nom}</td>
            <td>${r.motif||''}</td>
            <td>${r.statut}</td>
            <td>
              <button class="btn" data-action="start">Commencer</button>
              <button class="btn secondary" data-action="annuler">Annuler</button>
            </td>
          </tr>`).join('')}
          </tbody>
        </table>
      </div>
    `;

    document.querySelectorAll('#rdvTable button').forEach(btn=>{
      btn.addEventListener('click', async e=>{
        const tr = e.target.closest('tr'); const id = tr.dataset.id;
        const action = e.target.dataset.action;
        if(action==='annuler'){
          await api(`/rdv/${id}/annuler`, {method:'POST'});
          notify('RDV annulé');
          page_rdv_du_jour();
        } else if(action==='start'){
          await api(`/rdv/${id}/commencer`, {method:'POST'});
          notify('RDV démarré');
          page_rdv_du_jour();
        }
      });
    });
  }

  // Page: disponibilites
  async function page_disponibilites(){
    const disp = await api('/disponibilites');
    const container = document.getElementById('page-content');
    container.innerHTML = `
      <div class="header-row"><h2 class="h1">Disponibilités</h2>
        <div><button id="addDisp" class="btn">Ajouter une disponibilité</button></div>
      </div>
      <div class="card">
        <table class="table"><thead><tr><th>Date</th><th>Heures</th><th>Actions</th></tr></thead>
        <tbody id="dispBody">${(disp||[]).map(d=>`<tr data-id="${d.id}"><td>${d.date}</td><td>${d.heure}</td>
          <td><button class="btn secondary" data-action="del">Supprimer</button></td></tr>`).join('')}</tbody>
        </table>
      </div>
    `;
    $('#addDisp').addEventListener('click', ()=>{
      const modal = document.createElement('div');
      modal.innerHTML = `<div class="card" style="padding:18px"><h3>Nouvelle disponibilité</h3>
        <div class="form-row"><input id="d_date" class="input" type="date" /><input id="d_time" class="input" type="text" placeholder="ex: 10:00-12:00"/></div>
        <div style="margin-top:10px"><button class="btn" id="saveDisp">Enregistrer</button></div></div>`;
      document.getElementById('page-content').prepend(modal);
      $('#saveDisp').addEventListener('click', async ()=>{
        const date = $('#d_date').value; const heure=$('#d_time').value;
        await api('/disponibilites', {method:'POST', body: JSON.stringify({date,heure})});
        notify('Disponibilité ajoutée');
        page_disponibilites();
      });
    });

    document.querySelectorAll('button[data-action="del"]').forEach(b=>{
      b.addEventListener('click', async e=>{
        const id = e.target.closest('tr').dataset.id;
        await api(`/disponibilites/${id}`, {method:'DELETE'});
        notify('Disponibilité supprimée');
        page_disponibilites();
      });
    });
  }

  // Page: statistiques
  async function page_statistiques(){
    const stats = await api('/statistiques/full');
    const container = document.getElementById('page-content');
    container.innerHTML = `
      <div class="header-row"><h2 class="h1">Statistiques</h2></div>
      <div class="grid">
        <div class="card"><h3>Total RDV</h3><p>${stats?.total_rdv || 0}</p></div>
        <div class="card"><h3>RDV confirmés</h3><p>${stats?.rdv_valides || 0}</p></div>
        <div class="card"><h3>RDV annulés</h3><p>${stats?.rdv_annules || 0}</p></div>
      </div>
      <div style="margin-top:12px" class="card"><canvas id="statsChart" height="140"></canvas></div>
    `;
    const ctx = document.getElementById('statsChart').getContext('2d');
    new Chart(ctx, {
      type:'bar',
      data:{
        labels: stats?.by_week?.map(w=>w.week) || ['S1','S2','S3','S4'],
        datasets:[{label:'RDV',data:stats?.by_week?.map(w=>w.count)||[5,8,6,9]}]
      },
      options:{plugins:{legend:{display:false}}}
    });
  }

  // Page: profil
  async function page_profil(){
    const prof = await api('/profil');
    const container = document.getElementById('page-content');
    container.innerHTML = `
      <div class="header-row"><h2 class="h1">Mon profil</h2>
        <div><button id="saveProfile" class="btn">Enregistrer</button></div>
      </div>
      <div class="card">
        <div class="form-row">
          <input id="nom" class="input" placeholder="Nom" value="${prof?.nom || ''}" />
          <input id="email" class="input" placeholder="Email" value="${prof?.email || ''}" />
        </div>
        <div style="margin-top:10px"><textarea id="desc" class="input" placeholder="Description">${prof?.description||''}</textarea></div>
      </div>
    `;
    $('#saveProfile').addEventListener('click', async ()=>{
      const payload = {nom:$('#nom').value,email:$('#email').value,description:$('#desc').value};
      await api('/profil', {method:'PUT', body: JSON.stringify(payload)});
      notify('Profil mis à jour');
      loadProfile();
    });
  }

  // Page: patients
  async function page_patients(){
    const patients = await api('/patients');
    const container = document.getElementById('page-content');
    container.innerHTML = `
      <div class="header-row"><h2 class="h1">Patients</h2></div>
      <div class="card">
        <table class="table"><thead><tr><th>Nom</th><th>Email</th><th>Téléphone</th><th>Dernier RDV</th></tr></thead>
        <tbody>${(patients||[]).map(p=>`<tr><td>${p.nom}</td><td>${p.email}</td><td>${p.telephone||''}</td><td>${p.dernier_rdv||'-'}</td></tr>`).join('')}</tbody>
        </table>
      </div>
    `;
  }

  // Page: avis
  async function page_avis(){
    const avis = await api('/avis');
    const container = document.getElementById('page-content');
    container.innerHTML = `
      <div class="header-row"><h2 class="h1">Avis des patients</h2></div>
      <div class="card">
        ${(avis||[]).map(a=>`<div style="padding:12px;border-bottom:1px solid #f1f6fb">
          <strong>${a.patient_nom}</strong> <span class="small">${a.date}</span>
          <div class="small">Note: ${a.note}/5</div>
          <p>${a.commentaire}</p>
        </div>`).join('')}
      </div>
    `;
  }

  // Page: agenda
  async function page_agenda(){
    // Simple agenda list + nouvelle réservation (pour tests)
    const events = await api('/rdv'); // all rdv
    const container = document.getElementById('page-content');
    container.innerHTML = `
      <div class="header-row"><h2 class="h1">Agenda</h2>
        <div><button id="newRdv" class="btn">Ajouter RDV test</button></div>
      </div>
      <div class="card">
        <ul>${(events||[]).map(e=>`<li>${e.date} ${e.heure} - ${e.patient_nom} (${e.statut})</li>`).join('')}</ul>
      </div>
    `;
    $('#newRdv').addEventListener('click', async ()=>{
      // simple creation form
      const date = prompt('Date (YYYY-MM-DD)');
      const heure = prompt('Heure (HH:MM)');
      const patient = prompt('Nom du patient');
      if(date && heure && patient){
        await api('/rdv', {method:'POST', body: JSON.stringify({date,heure,patient_nom:patient})});
        notify('RDV ajouté');
        page_agenda();
      }
    });
  }

  // Page: chat (polling)
  async function page_chat(){
    const container = document.getElementById('page-content');
    container.innerHTML = `
      <div class="header-row"><h2 class="h1">Chat patients</h2></div>
      <div class="card">
        <div id="chatWindow" class="chat-window"></div>
        <div style="display:flex;gap:8px;margin-top:8px">
          <input id="chatMsg" class="input" placeholder="Message..." />
          <button id="sendChat" class="btn">Envoyer</button>
        </div>
      </div>
    `;

    const chatWindow = $('#chatWindow');
    const loadMessages = async () => {
      try {
        const msgs = await api('/chat/messages'); // returns [{from:'patient'|'me',text,ts}]
        chatWindow.innerHTML = msgs.map(m=>`<div class="msg ${m.from==='me'?'me':'other'}">${m.text}</div>`).join('');
        chatWindow.scrollTop = chatWindow.scrollHeight;
      } catch(e){}
    };

    $('#sendChat').addEventListener('click', async ()=>{
      const text = $('#chatMsg').value.trim(); if(!text) return;
      await api('/chat/send', {method:'POST', body: JSON.stringify({text})});
      $('#chatMsg').value = '';
      await loadMessages();
    });

    // polling every 3s
    await loadMessages();
    const poll = setInterval(loadMessages, 3000);
    // clear on navigate away (optional)
    window.addEventListener('beforeunload', ()=> clearInterval(poll));
  }

  // Router: detect body id and call page function
  const bodyId = document.body.id || document.getElementById('page-content')?.dataset.page || '';
  await loadProfile();
  try{
    if(bodyId.includes('dashboard')) await page_dashboard();
    else if(bodyId.includes('rdv_du_jour')) await page_rdv_du_jour();
    else if(bodyId.includes('disponibilites')) await page_disponibilites();
    else if(bodyId.includes('statistiques')) await page_statistiques();
    else if(bodyId.includes('profil')) await page_profil();
    else if(bodyId.includes('patients')) await page_patients();
    else if(bodyId.includes('avis')) await page_avis();
    else if(bodyId.includes('agenda')) await page_agenda();
    else if(bodyId.includes('chat')) await page_chat();
    else await page_dashboard(); // default
  } catch(e){
    console.error('Erreur initialisation page', e);
  }

  // Logout button behavior (calls gateway)
  $('#logoutBtn')?.addEventListener('click', async ()=>{
    try{ await api('/logout', {method:'POST'}); window.location.href = '/auth/connexion.html'; } catch(e){}
  });

})();
