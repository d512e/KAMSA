// static/js/filtre_vehicules.js

document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.vehicles-grid .card');

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            // 1. Gérer la classe active sur les boutons
            buttons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            // 2. Récupérer la catégorie sélectionnée
            const filterValue = this.getAttribute('data-filter');

            // 3. Filtrer les cartes
            cards.forEach(card => {
                const cardCategory = card.getAttribute('data-category');

                if (filterValue === 'all' || cardCategory === filterValue) {
                    card.style.display = 'block'; // Affiche le véhicule
                } else {
                    card.style.display = 'none';  // Masque le véhicule
                }
            });
        });
    });
});