function setLoadingImage() {
    const submitButton = document.getElementById('submit-button');
    const loadingImage = document.getElementById('loading-img');

    submitButton.style.display = 'none';
    loadingImage.style.display = 'block';
}