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
            if (!modal.contains(e.target) && !e.target.hasAttribute('data-modal')) {
                modal.classList.add('hide');
            }
        });
    }
}

function fileTypeError(message, id) {
    displayFlashMessage(message, "error");
    document.getElementById(id).value = null
}

function displayFlashMessage(message) {
    const flashContainer = document.getElementById("flash-container");
    flashContainer.innerHTML = 
    `<div id="modal" class="modal">
              <img src="/static/images/alert.png" width="44" height="38" />
              <span class="title">Oh snap!</span>
              <p>${message}</p>
              <div id="dismiss-button" class="button">Dismiss</div>
      </div>`;

    initializeModal();
}

document.addEventListener("DOMContentLoaded", initializeModal);