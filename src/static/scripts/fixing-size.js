document.addEventListener("DOMContentLoaded", function() {
    const card = document.getElementById("fixed-card");
    const subDiv = document.getElementsByClassName("fixed-sub-div");
    const cardInitialWidth = window.innerWidth * 0.5; // 50% de la largeur initiale de la fenêtre
    const cardInitialHeight = window.innerHeight * 0.7; // 60% de la hauteur initiale de la fenêtre
    const subDivInitialHeight = cardInitialHeight * 0.65; // 70% de la hauteur initiale de la carte
    card.style.width = `${cardInitialWidth}px`;
    card.style.height = `${cardInitialHeight}px`;
    for (let i = 0; i < subDiv.length; i++) {
        subDiv[i].style.height = `${subDivInitialHeight}px`;
    }

});