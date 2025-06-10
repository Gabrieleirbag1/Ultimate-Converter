# Ultimate-Converter

## Debug helper for spotdl container
bash `docker run --rm -v "$(pwd)/spotdl-errors:/root/.spotdl/errors" spotdl https://open.spotify.com/intl-fr/track/4aKkhZmKHRqW1mYKI0VTtC?si=6c64207e0ed14ba2`
bash `cat $(ls -t spotdl-errors/ffmpeg_error_*.txt | head -1)`