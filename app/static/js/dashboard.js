const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

allSideMenu.forEach(item=> {
	const li = item.parentElement;

	item.addEventListener('click', function () {
		allSideMenu.forEach(i=> {
			i.parentElement.classList.remove('active');
		})
		li.classList.add('active');
	})
});




// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');

menuBar.addEventListener('click', function () {
	sidebar.classList.toggle('hide');
})







const searchButton = document.querySelector('#content nav form .form-input button');
const searchButtonIcon = document.querySelector('#content nav form .form-input button .bx');
const searchForm = document.querySelector('#content nav form');

searchButton.addEventListener('click', function (e) {
	if(window.innerWidth < 576) {
		e.preventDefault();
		searchForm.classList.toggle('show');
		if(searchForm.classList.contains('show')) {
			searchButtonIcon.classList.replace('bx-search', 'bx-x');
		} else {
			searchButtonIcon.classList.replace('bx-x', 'bx-search');
		}
	}
})





if(window.innerWidth < 768) {
	sidebar.classList.add('hide');
} else if(window.innerWidth > 576) {
	searchButtonIcon.classList.replace('bx-x', 'bx-search');
	searchForm.classList.remove('show');
}


window.addEventListener('resize', function () {
	if(this.innerWidth > 576) {
		searchButtonIcon.classList.replace('bx-x', 'bx-search');
		searchForm.classList.remove('show');
	}
})



const switchMode = document.getElementById('switch-mode');

switchMode.addEventListener('change', function () {
	if(this.checked) {
		document.body.classList.add('dark');
	} else {
		document.body.classList.remove('dark');
	}
})
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

  // donner un id aux items existants + ajouter actions edit/delete
  list.querySelectorAll('li').forEach(li => {
    if (!li.dataset.id) li.dataset.id = crypto.randomUUID();
    const menu = li.querySelector('.bx-dots-vertical-rounded');
    if (menu) {
      const wrap = document.createElement('div');
      wrap.style.display = 'flex';
      wrap.style.gap = '6px';
      wrap.style.alignItems = 'center';
      wrap.innerHTML = `
        <i class='bx bx-edit-alt' title="Modifier"></i>
        <i class='bx bx-trash' title="Supprimer"></i>
      `;
      menu.replaceWith(wrap);
      wrap.querySelector('.bx-edit-alt').addEventListener('click', () => openEdit(li));
      wrap.querySelector('.bx-trash').addEventListener('click', () => removeItem(li));
    }
  });

  // Ouvrir modal en mode "ajout"
  btnAdd.addEventListener('click', () => {
    dialogTitle.textContent = 'Ajouter une tâche';
    taskId.value = '';
    taskTitle.value = '';
    taskStatus.value = 'completed';
    dialog.showModal();
    setTimeout(() => taskTitle.focus(), 50);
  });

  // Fermer modal
  [btnClose, btnCancel].forEach(b => b.addEventListener('click', () => dialog.close()));

  // Soumettre (ajout / édition)
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const id = taskId.value.trim();
    const title = taskTitle.value.trim();
    const status = taskStatus.value;

    if (!title) return;

    if (id) {
      // Édition
      const li = list.querySelector(`li[data-id="${id}"]`);
      if (li) {
        li.querySelector('p').textContent = title;
        li.classList.remove('completed','not-completed');
        li.classList.add(status);
      }
    } else {
      // Ajout
      const li = document.createElement('li');
      li.className = status;
      li.dataset.id = crypto.randomUUID();
      li.innerHTML = `
        <p>${title}</p>
        <div style="display:flex;gap:6px;align-items:center">
          <i class='bx bx-edit-alt' title="Modifier"></i>
          <i class='bx bx-trash' title="Supprimer"></i>
        </div>
      `;
      li.querySelector('.bx-edit-alt').addEventListener('click', () => openEdit(li));
      li.querySelector('.bx-trash').addEventListener('click', () => removeItem(li));
      list.prepend(li);
    }

    dialog.close();
  });

  // Fonctions utilitaires
  function openEdit(li) {
    dialogTitle.textContent = 'Modifier la tâche';
    taskId.value = li.dataset.id;
    taskTitle.value = li.querySelector('p').textContent.trim();
    taskStatus.value = li.classList.contains('completed') ? 'completed' : 'not-completed';
    dialog.showModal();
    setTimeout(() => taskTitle.focus(), 50);
  }

  function removeItem(li) {
    if (confirm('Supprimer cette tâche ?')) li.remove();
  }
});
