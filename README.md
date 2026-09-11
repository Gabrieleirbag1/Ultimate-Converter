# Ultimate-Converter

## Description

Ultimate-Converter is a powerful and versatile media conversion tool that allows users to effortlessly convert image, video, audio, vector and archive files between various formats. 
Additionally, you can download medias from few websites including Youtube, Spotify, Twitter, Instagram, Tiktok and Reddit.

## Installation
To install Ultimate-Converter, you can use the following command:

```bash
./install.sh
```

## Run Inkscape container
```bash
./src/inkscape.sh
```

## Usage
To use Ultimate-Converter, you can run the following command:
```bash
python3 src/app.py
```
Access the web interface at `http://localhost:8084` and follow the instructions to convert your media files or download from supported websites.

## Debug helper for spotdl container
bash `docker run --rm -v "$(pwd)/spotdl-errors:/root/.spotdl/errors" spotdl https://open.spotify.com/intl-fr/track/4aKkhZmKHRqW1mYKI0VTtC?si=6c64207e0ed14ba2`
bash `cat $(ls -t spotdl-errors/ffmpeg_error_*.txt | head -1)`

## Secrets

### Instagram
Get the instagram session file by logging in with your Instagram account using Instaloader. You can do this by running the following commands:
```bash
instaloader --login <instagram_username>
instaloader --load-cookies <browser> --sessionfile=<path/to/this/repo>/src/secrets/instaloader-session

sudo chown <user>:<group> src/secrets/instaloader-session # for apache deployment with mod_wsgi
```

### Spotify
To get the Spotify client ID and client secret, you need to create a Spotify Developer account and register an application. Follow these steps:
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
2. Log in with your Spotify account or create a new one if you don't have an account
3. Click on "Create an App" and fill in the required information (App name, description, etc.)
4. Once the app is created, you will be redirected to the app's dashboard. Here, you can find the "Client ID" and "Client Secret" under the "Settings" tab. Copy these values and save them in a secure location.
5. Find the file src/secrets/spotify.secrets and add the following lines, replacing <client_id> and <client_secret> with the values you copied from the Spotify Developer Dashboard:
```
CLIENT_ID=<client_id>
CLIENT_SECRET=<client_secret>
```

# Acknowledgments
- [Inkscape](https://inkscape.org/) - A powerful vector graphics editor used for converting vector files.
- [AutoTrace](https://github.com/autotrace/autotrace) - A tool for converting bitmap images to vector graphics.
- [SpotDL](https://github.com/spotdl/spotdl) - A command-line tool for downloading music from Spotify.
- [FFmpeg](https://ffmpeg.org/) - A multimedia framework used for converting audio and video files.
- [Youtube-DL](https://github.com/ytdl-org/youtube-dl) - A command-line program for downloading videos from YouTube and other websites.

# Author
- [@Missclick](https://www.github.com/Gabrieleirbag1) (Developer)  
  E-mail : gabrielgarronedev@gmail.com  
  Discord : missclick.net

# License
This project is licensed under the custom Ultimate-Converter Non-Commercial License - see the [LICENSE](LICENSE) file for details.
PLEASE do not sell or redistribute this software without permission from the author. For inquiries, please contact the author directly.