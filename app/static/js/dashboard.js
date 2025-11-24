console.log("✅ dashboard.js loaded");

// ==========================
// ✅ DARK MODE (Persistant)
// ==========================
document.addEventListener("DOMContentLoaded", () => {
  const switchMode = document.getElementById('switch-mode');
  const switchLabel = document.querySelector('.switch-mode');

  if (switchMode && switchLabel) {
    switchLabel.classList.add('no-transition');

    if (localStorage.getItem('dark-mode') === 'enabled') {
      document.body.classList.add('dark');
      switchMode.checked = true;
    }

    setTimeout(() => {
      switchLabel.classList.remove('no-transition');
    }, 50);

    switchMode.addEventListener('change', function () {
      if (this.checked) {
        document.body.classList.add('dark');
        localStorage.setItem('dark-mode', 'enabled');
      } else {
        document.body.classList.remove('dark');
        localStorage.setItem('dark-mode', 'disabled');
      }
    });
  }
});

// ==========================
// ✅ SIDEBAR PERSISTANTE
// ==========================
document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById('sidebar');
  const menuBar = document.querySelector('#content nav .bx.bx-menu');

  if (sidebar) {
    if (localStorage.getItem('sidebar') === 'hidden') {
      sidebar.classList.add('hide');
    }

    if (menuBar) {
      menuBar.addEventListener('click', () => {
        sidebar.classList.toggle('hide');

        localStorage.setItem(
          'sidebar',
          sidebar.classList.contains('hide') ? 'hidden' : 'shown'
        );
      });
    }
  }
});

/// ==========================
// ✅ TASKS DASHBOARD
// ==========================
document.addEventListener('DOMContentLoaded', () => {
  const list = document.getElementById('todoList');
  const btnAdd = document.getElementById('todoAddBtn');

  const dialog = document.getElementById('taskDialog');
  const dialogTitle = document.getElementById('dialogTitle');
  const taskId = document.getElementById('taskId');
  const taskTitle = document.getElementById('taskTitle');
  const taskStatus = document.getElementById('taskStatus');
  const btnClose = document.getElementById('closeDialog');
  const btnCancel = document.getElementById('cancelDialog');
  const form = document.getElementById('taskForm');

  // ✅ Ajouter une tâche
  btnAdd.addEventListener('click', () => {
    dialogTitle.textContent = 'Ajouter une tâche';
    taskId.value = '';
    taskTitle.value = '';
    taskStatus.value = 'complétée';
    dialog.showModal();
  });

  // ✅ Fermer modal
  [btnClose, btnCancel].forEach(b =>
    b.addEventListener('click', () => dialog.close())
  );

  // ✅ Soumission (AJAX vers Flask → RPC)
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const id = taskId.value.trim();
    const titre = taskTitle.value.trim();
    const statut = taskStatus.value;

    if (!titre) return;

    // ✅ EDIT
    if (id) {
      const res = await fetch(`/admin/taches/edit/${id}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({titre, statut})
      });

      if (res.ok) location.reload();
      return;
    }

    // ✅ ADD
    const res = await fetch(`/admin/taches/add`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({titre, statut})
    });

    if (res.ok) location.reload();

    dialog.close();
  });

  // ✅ Event Delegation (EDIT + DELETE)
  list.addEventListener('click', async (e) => {
    const li = e.target.closest('li');
    if (!li) return;
    const id = li.dataset.id;

    // ✏️ Edit
    if (e.target.classList.contains('bx-edit-alt')) {
      dialogTitle.textContent = 'Modifier la tâche';
      taskId.value = id;
      taskTitle.value = li.querySelector('p').textContent.trim();
      taskStatus.value = li.classList.contains('completed') ? 'complétée' : 'non_complétée';
      dialog.showModal();
    }

    // 🗑 Delete
    if (e.target.classList.contains('bx-trash')) {
      if (confirm("Supprimer cette tâche ?")) {
        const res = await fetch(`/admin/taches/delete/${id}`, {
          method: "POST"
        });

        if (res.ok) li.remove();
      }
    }
  });
});
