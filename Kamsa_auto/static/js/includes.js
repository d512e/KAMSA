document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-include]").forEach((slot) => {
        const file = slot.getAttribute("data-include");

        if(!file) return;

        fetch(`express_app/templates/user/${file}.html`)
            .then((response) => (response.ok ? response.text() : ""))
            .then((html) => {
            slot.innerHTML = html;
        })
        .catch((error) => {
            console.log(`Chargement de ${file}.html impossible`, error);
        });
    });
});