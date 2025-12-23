
document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll(".animated-title, .animated-text, .btn-main, .features h2, .about h2, .about p");
    elements.forEach((el, index) => {
        setTimeout(() => el.classList.add("active"), index * 150);
    });
});
