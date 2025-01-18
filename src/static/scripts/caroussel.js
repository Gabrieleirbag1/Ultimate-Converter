function handleCaroussel() {
    const cards = document.querySelectorAll('.info-div .index-card');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    let currentIndex = 0;

    function updateCarousel() {
        cards.forEach((card, index) => {
            card.style.display = 'none';
            if (index === currentIndex) {
                card.style.display = 'block';
            }
        });
    }

    function checkViewport() {
        if (window.innerWidth <= 768) {
            prevBtn.style.display = 'block';
            nextBtn.style.display = 'block';
            updateCarousel();
        } else {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
            cards.forEach(card => card.style.display = 'block');
            document.querySelector('.info-div').style.transform = 'none';
        }
    }

    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = cards.length - 1;
        }
        updateCarousel();
    });

    nextBtn.addEventListener('click', () => {
        if (currentIndex < cards.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0;
        }
        updateCarousel();
    });

    window.addEventListener('resize', checkViewport);
    checkViewport();
}

document.addEventListener('DOMContentLoaded', handleCaroussel);