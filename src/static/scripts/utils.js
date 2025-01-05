const formats = {
    audio: ['mp3', 'aac', 'ac3', 'flac', 'wav', 'ogg', 'wma', 'aiff', 'dts', 'eac3', 'm4a', 'mp2', 'opus', 'pcm'],
    video: ['mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'webm', '3gp', 'asf', 'm4v', 'ts', 'm2ts', 'vob', 'rm', 'swf'],
    image: ['jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'pgm', 'ppm', 'pam', 'tga'],
    vector: ['svg', 'pdf', 'eps', 'svgz', 'dxf', 'emf', 'wmf', 'xaml', 'fxg', 'hpgl', 'odg', 'ps', 'sif'],
    autotrace_vector: ['svg (autotrace)', 'pdf (autotrace)', 'fig (autotrace)', 'ai (autotrace)', 'sk (autotrace)', 'p2e (autotrace)', 'mif (autotrace)', 'er (autotrace)', 'eps (autotrace)', 'emf (autotrace)', 'dxf (autotrace)', 'drd2 (autotrace)', 'cgm (autotrace)'],
    archive: ['7z', 'cb7', 'cbt', 'cbz', 'cpio', 'iso', 'jar', 'tar', 'tar.bz2', 'tar.gz', 'tar.lzma', 'tar.xz', 'tbz2', 'tgz', 'txz', 'zip']
};

let types = [];
