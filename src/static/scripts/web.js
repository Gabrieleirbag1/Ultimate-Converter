const formats = {
    audio: ['mp3', 'aac', 'ac3', 'flac', 'wav', 'ogg', 'wma', 'aiff', 'dts', 'eac3', 'm4a', 'mp2', 'opus', 'pcm'],
    video: ['mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'webm', '3gp', 'asf', 'm4v', 'ts', 'm2ts', 'vob', 'rm', 'swf'],
    image: ['jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'pgm', 'ppm', 'pam', 'tga'],
    vector: ['svg', 'pdf', 'eps', 'svgz', 'dxf', 'emf', 'wmf', 'xaml', 'fxg', 'hpgl', 'odg', 'ps', 'sif'],
    autotrace_vector: ['svg (autotrace)', 'pdf (autotrace)', 'fig (autotrace)', 'ai (autotrace)', 'sk (autotrace)', 'p2e (autotrace)', 'mif (autotrace)', 'er (autotrace)', 'eps (autotrace)', 'emf (autotrace)', 'dxf (autotrace)', 'drd2 (autotrace)', 'cgm (autotrace)'],
    archive: ['7z', 'cb7', 'cbt', 'cbz', 'cpio', 'iso', 'jar', 'tar', 'tar.bz2', 'tar.gz', 'tar.lzma', 'tar.xz', 'tbz2', 'tgz', 'txz', 'zip']
};

let types = [];

function checkUrlWebsite(url) {
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
        return "Youtube";
    } else if (url.includes('twitter.com') || url.includes('x.com')) {
        return "Twitter";
    } else if (url.includes('instagram.com')) {
        return "Instagram";
    } else if (url.includes('spotify.com')) {
        return "Spotify";
    } else {
        return null;
    }
}

function handleFileUpload() {
    const file_type = document.getElementById('file-type');
    const file_preview = document.getElementById('file-preview');
    const download_div = document.getElementById('web-div');
    const h4_filename = document.getElementById('h4-filename');
    const url = document.getElementById("url").value;
    
    media = checkUrlWebsite(url);

    file_type.innerHTML = '';

    if (media == "Youtube"){
        types = ["Video", "Audio"]
    }

    else if (media == "Instagram"){
        types = ["Image", "Video", "Audio"]
    }

    else if (media == "Twitter"){
        types = ["Video", "Audio"]
    }

    else if (media == "Spotify"){
        types = ["Audio"]
    }

    else{
        displayFlashMessage("Media not supported. Please enter a valid URL.");
        // delete the file from the input
        document.getElementById('url').value = null
        return;
    }

    h4_filename.textContent = "Download from " + media;
    download_div.style.display = 'none';
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

function manageFormEvents() {
    const urlInput = document.getElementById("url");
    const form = document.getElementById("web-form");

    urlInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            handleFileUpload();
        }
    });

    form.addEventListener("submit", function(event) {
        event.preventDefault();
        handleFileUpload();
    });
}

document.addEventListener("DOMContentLoaded", function() {
    manageFormEvents();
});