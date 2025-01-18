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

function checkInstagramUrl(url) {
    if (url.includes('instagram.com')) {
        if (url.match(/\/reel\//)) {
            return "Reel";
        } else if (url.match(/\/p\//)) {
            return "Photo";
        } else if (url.match(/\/tv\//)) {
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

    if (media == "Youtube"){
        types = ["Video", "Audio"]
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
        types = ["Video", "Audio"]
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
    file_format.innerHTML = '';

    formats[file_type].forEach(format => {
        const option = document.createElement('option');
        option.value = format;
        option.textContent = format;
        file_format.appendChild(option);
    });
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