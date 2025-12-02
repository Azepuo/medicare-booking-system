const socket = io(); // Socket.IO

socket.on('connect', () => console.log("Connecté au serveur WebSocket"));

socket.on('notification', (data) => {
    const container = document.getElementById("notifications");
    if (!container) return;

    const div = document.createElement("div");
    div.className = "notification-item";
    div.textContent = data.message;
    div.onclick = () => div.remove();
    container.prepend(div);
});

// Polling notifications (optionnel si pas WebSocket)
async function fetchNotifications() {
    try {
        const result = await fetch("/api/rpc", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ method: "get_notifications" })
        }).then(r => r.json());

        if (result.success) {
            const container = document.getElementById("notifications");
            container.innerHTML = "";
            result.notifications.forEach(n => {
                const div = document.createElement("div");
                div.className = "notification-item";
                div.textContent = n.message;
                container.appendChild(div);
            });
        }
    } catch (err) { console.error(err); }
}

setInterval(fetchNotifications, 10000);
