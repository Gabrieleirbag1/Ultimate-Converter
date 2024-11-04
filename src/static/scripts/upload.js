const formats = {
    audio: ['mp3', 'aac', 'ac3', 'flac', 'wav', 'ogg', 'wma', 'alac', 'aiff', 'amr', 'dts', 'eac3', 'm4a', 'mp2', 'opus', 'pcm', 'vorbis'],
    video: ['mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'webm', '3gp', 'asf', 'm4v', 'ts', 'm2ts', 'vob', 'rm', 'swf'],
    image: ['jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'pgm', 'ppm', 'pam', 'pnm', 'tga'],
    vector: ['svg', 'eps', 'pdf', 'ai', 'emf', 'wmf'],
    subtitle: ['srt', 'ass', 'ssa', 'sub', 'vtt', 'stl', 'dfxp', 'sami', 'mpl2', 'pjs', 'jacosub'],
    archive: ['tar', 'zip', 'gz', 'bz2', 'rar', '7z']
};

let types = [];

function handleFileUpload() {
    const file_type = document.getElementById('file-type');
    const file_preview = document.getElementById('file-preview');

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
        window.alert("File type not supported");
        // delete the file from the input
        document.getElementById('file-input').value = null
        return;
    }

    file_preview.style.display = 'block';

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