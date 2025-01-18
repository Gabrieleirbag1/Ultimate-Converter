function copyToClipboard() {
    var copyText = document.getElementById('share-link');
    copyText.select();
    document.execCommand('copy');

    var shareIcon = document.getElementById('share-icon');
    var checkIcon = document.getElementById('check-icon');

    shareIcon.style.display = 'none';
    checkIcon.style.display = 'block';

    setTimeout(function() {
        checkIcon.style.display = 'none';
        shareIcon.style.display = 'block';
    }, 1500);
}