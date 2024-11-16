function initializeModal() {
    const button = document.getElementById("dismiss-button");
    const modal = document.getElementById("modal");

    if (button && modal) {
        button.addEventListener('click', function() {
            modal.classList.add('hide');
        });

        window.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                modal.classList.add('hide');
            }
        });

        document.addEventListener('click', e => {
            if (!modal.contains(e.target)) {
                modal.classList.add('hide');
            }
        });
    }
}

// Call the function to set up the modal when the script is first loaded
document.addEventListener("DOMContentLoaded", initializeModal);