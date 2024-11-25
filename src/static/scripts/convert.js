const formats = {
    audio: ['mp3', 'aac', 'ac3', 'flac', 'wav', 'ogg', 'wma', 'alac', 'aiff', 'amr', 'dts', 'eac3', 'm4a', 'mp2', 'opus', 'pcm', 'vorbis'],
    video: ['mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'webm', '3gp', 'asf', 'm4v', 'ts', 'm2ts', 'vob', 'rm', 'swf'],
    image: ['jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'pgm', 'ppm', 'pam', 'pnm', 'tga'],
    vector: ['svg', 'pdf', 'eps', 'ps', 'dxf', 'geojson', 'pdfpage', 'pgm', 'gimppath', 'xfig'],
    subtitle: ['srt', 'ass', 'ssa', 'sub', 'vtt', 'stl', 'dfxp', 'sami', 'mpl2', 'pjs', 'jacosub'],
    archive: ['tar', 'zip', 'gz', 'bz2', 'rar', '7z']
};

let types = [];

function handleFileUpload() {
    const file_type = document.getElementById('file-type');
    const file_preview = document.getElementById('file-preview');
    const drop_area = document.getElementById('drop-area');
    const h4_filename = document.getElementById('h4-filename');

    file_name = document.getElementById('file-input').files[0].name;
    const extension = file_name.split(".").pop();
    let file_category = null;

    for (const category in formats) {
        if (formats[category].includes(extension)) {
            file_category = category;
            break;
        }
    }

    file_type.innerHTML = '';

    if (file_category == "image"){
        types = ["Image", "Video", "Vector"]
    }
    else if (file_category == "video"){
        types = ["Video", "Image", "Audio"]        
    }
    else if (file_category == "audio"){
        types = ["Audio", "Video"]
    }
    else if (file_category == "vector"){
        types = ["Vector", "Image"]
    }
    else if (file_category == "subtitle"){
        types = ["Subtitle"]
    }
    else if (file_category == "archive"){
        types = ["Archive"]
    }
    else{
        displayFlashMessage("Invalid file format. Please upload a valid file format.");
        // delete the file from the input
        document.getElementById('file-input').value = null
        return;
    }

    h4_filename.textContent = file_name;
    drop_area.style.display = 'none';
    file_preview.style.display = 'flex';

    types.forEach(format => {
        const option = document.createElement('option');
        option.value = format;
        option.textContent = format;
        file_type.appendChild(option);
    })
    updateFormats();
}

function updateFormats() {
    const file_type = document.getElementById('file-type').value.toLowerCase();
    const file_format = document.getElementById('file-format');
    file_format.innerHTML = '';

    formats[file_type].forEach(format => {
        const option = document.createElement('option');
        option.value = format;
        option.textContent = format;
        file_format.appendChild(option);
    });
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
    document.getElementById("script_file").value = "";
  }

document.addEventListener("DOMContentLoaded", function() {
    const dropBox = document.getElementById("drop-box"),
        button = document.getElementById("btn-choose-file"),
        input = document.getElementById("file-input");

    button.onclick = () => {
        input.click();
    };

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropBox.addEventListener(eventName, preventDefaults, false)
        document.body.addEventListener(eventName, preventDefaults, false)
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropBox.addEventListener(eventName, highlight, false)
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropBox.addEventListener(eventName, unhighlight, false)
    });

    // Handle dropped files
    dropBox.addEventListener('drop', handleDrop, false);

    function preventDefaults(e) {
        e.preventDefault()
        e.stopPropagation()
    }

    function highlight(e) {
        dropBox.classList.add('highlight')
    }

    function unhighlight(e) {
        dropBox.classList.remove('highlight')
    }

    function handleDrop(e) {
        const dt = e.dataTransfer
        const files = dt.files

        input.files = files;
        handleFileUpload();
    }
});

