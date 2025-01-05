const formats = {
    audio: ['mp3', 'aac', 'ac3', 'flac', 'wav', 'ogg', 'wma', 'aiff', 'dts', 'eac3', 'm4a', 'mp2', 'opus', 'pcm'],
    video: ['mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'webm', '3gp', 'asf', 'm4v', 'ts', 'm2ts', 'vob', 'rm', 'swf'],
    image: ['jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'pgm', 'ppm', 'pam', 'tga'],
    vector: ['svg', 'pdf', 'eps', 'svgz', 'dxf', 'emf', 'wmf', 'xaml', 'fxg', 'hpgl', 'odg', 'ps', 'sif'],
    autotrace_vector: ['svg (autotrace)', 'pdf (autotrace)', 'fig (autotrace)', 'ai (autotrace)', 'sk (autotrace)', 'p2e (autotrace)', 'mif (autotrace)', 'er (autotrace)', 'eps (autotrace)', 'emf (autotrace)', 'dxf (autotrace)', 'drd2 (autotrace)', 'cgm (autotrace)'],
    archive: ['7z', 'cb7', 'cbt', 'cbz', 'cpio', 'iso', 'jar', 'tar', 'tar.bz2', 'tar.gz', 'tar.lzma', 'tar.xz', 'tbz2', 'tgz', 'txz', 'zip']
};

let types = [];

function handleFileUpload() {
    const file_type = document.getElementById('file-type');
    const file_preview = document.getElementById('file-preview');
    const drop_area = document.getElementById('drop-area');
    const h4_filename = document.getElementById('h4-filename');

    const file = document.getElementById('file-input').files[0];
    const file_name = file.name;
    const extension = getExtension(file_name);
    let file_category = null;

    for (const category in formats) {
        if (formats[category].includes(extension)) {
            file_category = category;
            break;
        }
    }

    file_type.innerHTML = '';

    if (file_category == "image") {
        types = ["Image", "Video", "Vector"];
        formats.vector = formats.vector.concat(formats.autotrace_vector);
    }
    else if (file_category == "video") {
        types = ["Video", "Image", "Audio"];
    }
    else if (file_category == "audio") {
        types = ["Audio", "Video"];
    }
    else if (file_category == "vector") {
        types = ["Vector", "Image"];
    }
    else if (file_category == "archive") {
        types = ["Archive"];
    }
    else {
        displayFlashMessage("Invalid file format. Please upload a valid file format.");
        // delete the file from the input
        document.getElementById('file-input').value = null;
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
    });
    updateFormats();
}

function getExtension(fileName) {
    const parts = fileName.split('.');
    if (parts.length > 1) {
        const possibleExtension = parts.slice(-2).join('.');
        if (formats.archive.includes(possibleExtension)) {
            return possibleExtension;
        }
    }
    return parts.pop();
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

document.addEventListener("DOMContentLoaded", function() {
    const dropBox = document.getElementById("drop-box"),
        button = document.getElementById("btn-choose-file"),
        input = document.getElementById("file-input");

    button.onclick = () => {
        input.click();
    };

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropBox.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropBox.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropBox.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropBox.addEventListener('drop', handleDrop, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropBox.classList.add('highlight');
    }

    function unhighlight(e) {
        dropBox.classList.remove('highlight');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        input.files = files;
        handleFileUpload();
    }
});