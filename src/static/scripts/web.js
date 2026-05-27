function checkUrlWebsite(url) {
    const lowerUrl = url.toLowerCase();
    if (lowerUrl.includes('youtube') || lowerUrl.includes('youtu.be')) {
        return "Youtube";
    } else if (lowerUrl.includes('tiktok')) {
        return "TikTok";
    } else if (lowerUrl.includes('reddit') || lowerUrl.includes('redd.it')) {
        return "Reddit";
    } else if (lowerUrl.includes('twitter') || lowerUrl.includes('x.com')) {
        return "Twitter";
    } else if (lowerUrl.includes('instagram')) {
        return "Instagram";
    } else if (lowerUrl.includes('spotify')) {
        return "Spotify";
    } else {
        return null;
    }
}

function checkInstagramUrl(url) {
    const lowerUrl = url.toLowerCase();
    if (lowerUrl.includes('instagram')) {
        if (lowerUrl.match(/\/reel\//)) {
            return "Reel";
        } else if (lowerUrl.match(/\/p\//)) {
            return "Photo";
        } else if (lowerUrl.match(/\/tv\//)) {
            return "Video";
        } else {
            return "Unknown";
        }
    }
    return null;
}

function handleFileUpload() {
    const file_type = document.getElementById('file-type');
    const file_preview = document.getElementById('file-preview');
    const download_div = document.getElementById('web-div');
    const h4_filename = document.getElementById('h4-filename');
    const url = document.getElementById("url").value;
    
    media = checkUrlWebsite(url);

    file_type.innerHTML = '';

    if (media == "Youtube" || media == "TikTok" || media == "Reddit"){
        types = ["Video", "Audio", "Image"]
    }

    else if (media == "Instagram"){
        if (checkInstagramUrl(url) == "Photo"){
            types = ["Image", "Video"]
        }
        else if (checkInstagramUrl(url) == "Unknown"){
            fileTypeError("Invalid Instagram URL. Please enter a valid URL.", "url");
            return;
        }
        else {
            types = ["Video", "Audio", "Image"]
        }
    }

    else if (media == "Twitter"){
        types = ["Video", "Audio", "Image"]
    }

    else if (media == "Spotify"){
        types = ["Audio"]
    }

    else{
        fileTypeError("Media not supported. Please enter a valid URL.", "url");
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
    const resolution_div = document.getElementById('resolution-div');
    const codec_div = document.getElementById('codec-div');

    file_format.innerHTML = '';

    formats[file_type].forEach(format => {
        const option = document.createElement('option');
        option.value = format;
        option.textContent = format;
        file_format.appendChild(option);
    });

    if (resolution_div && codec_div) {
        if ((media === "Youtube") && file_type === "video") {
            resolution_div.style.display = 'flex';
            codec_div.style.display = 'flex';
        } else {
            resolution_div.style.display = 'none';
            codec_div.style.display = 'none';
        }
    }
}

function handleEnterEvent() {
    const urlInput = document.getElementById("url");

    urlInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            handleFileUpload();
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    handleEnterEvent();
});