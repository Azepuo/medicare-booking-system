console.log("dashboard.js loaded ✅");

document.addEventListener("DOMContentLoaded", () => {
  const switchMode = document.getElementById('switch-mode');
  const switchLabel = document.querySelector('.switch-mode');
  const sidebar = document.getElementById('sidebar');
  const menuBar = document.querySelector('#content nav .bx.bx-menu');

  /* ✅ DARK MODE */
  if (switchMode && switchLabel) {

    // Désactiver l'animation au chargement
    switchLabel.classList.add('no-transition');

    // Appliquer l'état sauvegardé
    if (localStorage.getItem('dark-mode') === 'enabled') {
      document.body.classList.add('dark');
      switchMode.checked = true;
    } else {
      document.body.classList.remove('dark');
      switchMode.checked = false;
    }

    // Réactiver l'animation
    setTimeout(() => {
      switchLabel.classList.remove('no-transition');
    }, 50);

    // Changement utilisateur
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

  /* ✅ SIDEBAR PERSISTANTE */
  if (sidebar) {
    // Appliquer l'état sauvegardé
    if (localStorage.getItem('sidebar') === 'hidden') {
      sidebar.classList.add('hide');
    } else {
      sidebar.classList.remove('hide');
    }

    // Sauvegarder l'état au clic
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
