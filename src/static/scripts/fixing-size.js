function adjustHeight() {
    const card = document.getElementById("fixed-card");
    const subDiv = document.getElementsByClassName("fixed-sub-div");
    const cardInitialWidth = window.innerWidth * 0.5; // 50% de la largeur initiale de la fenêtre
    const subDivInitialHeight = window.innerHeight * 0.45; // 70% de la hauteur initiale de la carte
    card.style.width = `${cardInitialWidth}px`;
    for (let i = 0; i < subDiv.length; i++) {
        subDiv[i].style.height = `${subDivInitialHeight}px`;
    }
}

document.addEventListener("DOMContentLoaded", function() {
    adjustHeight();
    window.addEventListener("resize", adjustHeight);
});