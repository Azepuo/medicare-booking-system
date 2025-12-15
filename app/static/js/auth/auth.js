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

    // Toujours récupérer JSON, même en cas d'erreur 400 ou 500
    const data = await response.json();
    data.status = response.status;
    return data;
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

    if (!email || !password) {
        showError("Veuillez remplir tous les champs.", "login");
        return;
    }

    try {
        const result = await rpcCall("login", { email, password });
        console.log(result); // Voir le retour du backend

        if (!result.success) {
            showError(result.message || "Email ou mot de passe incorrect", "login");
        } else {
            window.location.href = result.redirect; // Redirection selon rôle
        }
    } catch (err) {
        showError("Erreur serveur.", "login");
        console.error(err);
    }
}

// ---------------- REGISTER ----------------
async function registerUser() {
    clearError("register");
    const fullname = document.getElementById("register_fullname").value.trim();
    const email = document.getElementById("register_email").value.trim();
    const tele = document.getElementById("register_tele")?.value.trim() || "";
    const password = document.getElementById("register_password").value.trim();
    const confirm = document.getElementById("register_confirm_password").value.trim();

    if (!fullname || !email || !tele || !password || !confirm) {
        showError("Veuillez remplir tous les champs.", "register");
        return;
    }
    if (password !== confirm) {
        showError("Les mots de passe ne correspondent pas.", "register");
        return;
    }

    try {
        const result = await rpcCall("register", { fullname, email, tele, password, confirm_password: confirm });
        console.log(result);

        if (!result.success) {
            showError(result.message || "Erreur inscription", "register");
        } else {
            window.location.href = "/login"; // Redirection vers login après inscription
        }
    } catch (err) {
        showError("Erreur serveur.", "register");
        console.error(err);
    }
}
