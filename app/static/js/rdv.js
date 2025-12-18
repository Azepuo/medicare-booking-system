document.addEventListener("DOMContentLoaded", function () {

    let disponibilites = [];

    const medecinSelect = document.getElementById("medecin_id");
    const dateInput = document.getElementById("date_rdv");
    const heureInput = document.getElementById("heure_rdv");

    // 🔒 Sécurité : si les champs n'existent pas, on sort
    if (!medecinSelect || !dateInput || !heureInput) {
        console.warn("RDV JS: champs manquants dans le DOM");
        return;
    }

    // =========================
    // 🔹 Charger disponibilités
    // =========================
    function chargerDisponibilites(medecinId) {
        if (!medecinId) {
            disponibilites = [];
            return;
        }

        fetch(`/admin/rendez_vous/dispos/${medecinId}`)
            .then(res => res.json())
            .then(data => {
                // Support {dates: []} OU []
                disponibilites = data.dates || data || [];
                console.log("Disponibilités chargées:", disponibilites);
            })
            .catch(err => {
                console.error("Erreur chargement disponibilités:", err);
                disponibilites = [];
            });
    }

    // =========================
    // 🔹 Changement médecin
    // =========================
    medecinSelect.addEventListener("change", function () {
        chargerDisponibilites(this.value);
        dateInput.value = "";
        heureInput.value = "";
    });

    // =========================
    // 🔹 Vérifier date
    // =========================
    dateInput.addEventListener("change", function () {
        if (!this.value || disponibilites.length === 0) return;

        const selectedDate = new Date(this.value + "T00:00:00");
        const dayName = selectedDate.toLocaleDateString("en-US", {
            weekday: "long"
        });

        const dispoJour = disponibilites.find(d => d.jour_semaine === dayName);

        if (!dispoJour) {
            alert("⚠️ Ce médecin n'est pas disponible ce jour.");
            this.value = "";
            heureInput.value = "";
        }
    });

    // =========================
    // 🔹 Vérifier heure
    // =========================
    heureInput.addEventListener("change", function () {
        const heure = this.value;
        const dateValue = dateInput.value;

        if (!dateValue || !heure || disponibilites.length === 0) return;

        const selectedDate = new Date(dateValue + "T00:00:00");
        const dayName = selectedDate.toLocaleDateString("en-US", {
            weekday: "long"
        });

        const dispoJour = disponibilites.find(d => d.jour_semaine === dayName);
        if (!dispoJour) return;

        if (heure < dispoJour.heure_debut || heure > dispoJour.heure_fin) {
            alert(
                `⚠️ Heure invalide.\nDisponible entre ${dispoJour.heure_debut} et ${dispoJour.heure_fin}`
            );
            this.value = "";
        }
    });

    // =========================
    // 🔹 Mode édition : auto-load
    // =========================
    if (medecinSelect.value) {
        chargerDisponibilites(medecinSelect.value);
    }

});
