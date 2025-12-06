document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    if (loginForm) loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        await loginUser();
    });

    const registerForm = document.getElementById("registerForm");
    if (registerForm) registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        await registerUser();
    });
});

// ---------------- RPC CALL ----------------
async function rpcCall(method, params = {}) {
    const response = await fetch("/api/rpc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ method, params })
    });
    return response.json();
}

// ---------------- UTILITAIRES ----------------
function showError(message, type="login") {
    const errorDiv = document.getElementById(type + "_error");
    errorDiv.textContent = message;
    errorDiv.style.display = "block";
}

function clearError(type="login") {
    const errorDiv = document.getElementById(type + "_error");
    errorDiv.textContent = "";
    errorDiv.style.display = "none";
}

// ---------------- LOGIN ----------------
async function loginUser() {
    clearError("login");
    const email = document.getElementById("login_email").value.trim();
    const password = document.getElementById("login_password").value.trim();
    const roleElem = document.getElementById("login_role");
    const role = roleElem ? roleElem.value : "patient"; // rôle choisi par l'utilisateur

    if (!email || !password) {
        showError("Veuillez remplir tous les champs.", "login");
        return;
    }

    try {
        const result = await rpcCall("login", { email, password, role });
        if (!result.success) showError(result.message || "Email ou mot de passe incorrect", "login");
        else window.location.href = result.redirect || "/home"; // redirection selon RPC
    } catch (err) {
        showError("Erreur serveur.", "login");
        console.error(err);
    }
}


// ---------------- REGISTER (CORRIGÉ) ----------------
async function registerUser() {
    clearError("register");
    const fullname = document.getElementById("register_fullname").value.trim();
    const email = document.getElementById("register_email").value.trim();
    
    // 🛠️ CORRECTION 1 : Récupérer le champ téléphone (ID: register_tele d'après le HTML)
    const teleElem = document.getElementById("register_tele");
    const tele = teleElem ? teleElem.value.trim() : ""; 
    
    const password = document.getElementById("register_password").value.trim();
    const confirm = document.getElementById("register_confirm_password").value.trim();
    const roleElem = document.getElementById("register_role");
    const role = roleElem ? roleElem.value : "patient"; // par défaut patient

    // 🛠️ CORRECTION 2 : Inclure 'tele' dans la validation
    if (!fullname || !email || !tele || !password || !confirm) { 
        showError("Veuillez remplir tous les champs.", "register");
        return;
    }
    if (password !== confirm) {
        showError("Les mots de passe ne correspondent pas.", "register");
        return;
    }

    try {
        let method = "register"; // patients
        if (role === "medecin") method = "register_medecin"; // médecins → RPC spécifique

        const result = await rpcCall(method, {
            fullname,
            email,
            tele, // 🛠️ CORRECTION 3 : Ajouter le téléphone
            password,
            confirm_password: confirm
        });

        if (!result.success) showError(result.message || "Erreur inscription", "register");
        else window.location.href = "/login";

    } catch (err) {
        showError("Erreur serveur.", "register");
        console.error(err);
    }
}