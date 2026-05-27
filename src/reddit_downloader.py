import os
import re
import requests
from urllib.parse import urlparse, parse_qs, unquote
from tqdm import tqdm
from logs import log
from base_downloader import BaseDownloader

REDDIT_HEADERS = {
    "User-Agent": "python:reddit-downloader:v1.0 (Ultimate Converter)"
}

class RedditDownloader(BaseDownloader):
    """Class to download reddit media

    :param str url: URL of the reddit media
    :param str output_path: Path to save the downloaded media
    :param str format: Format to convert the media to
    :param str final_file_name: Final name of the downloaded file
    """
    def __init__(self, url: str, output_path: str, format: str = "mp4") -> None:
        super().__init__(url, output_path, format)
        self.final_file_name: str
        self.medias_list: list[str] = []

    def download(self):
        """Download a reddit media file using direct requests."""
        download_url = self.normalize_url(self.url)
        extension = self.get_extension(download_url)
        self.generate_file_name(os.path.basename(download_url), extension)
        self.download_file(download_url, self.final_file_name)
        self.convert_file(extension)

    def normalize_url(self, url: str) -> str:
        """
        Normalize Reddit URLs into a directly downloadable form.

        Supported input types:
        1. v.redd.it / hosted video post  → yt-dlp
        2. reddit.com/r/.../s/<id>        → short share link, resolve via JSON API
        3. reddit.com/r/.../comments/<id>/comment/<cid>  → comment, resolve via JSON API
        4. reddit.com/r/.../comments/<id>/...  → post, resolve via JSON API
        5. reddit.com/media?url=<encoded> → unwrap, then treat as preview URL
        6. preview.redd.it/...            → ensure format=mp4 for GIFs
        7. i.redd.it/...                  → direct static image, pass through
        """
        parsed = urlparse(url)
        netloc = parsed.netloc
        path = parsed.path

        # ── 1. Hosted Reddit video (v.redd.it or is_video post) ──────────────
        if "v.redd.it" in netloc:
            # Need to import inside method to avoid circular dependency issues if any
            from youtube_downloader import YoutubeDownloader
            YoutubeDownloader(url, self.output_path, format=self.format).download_video()
            return url  # already handled

        # ── 2. Short share link  reddit.com/r/<sub>/s/<id> ───────────────────
        if re.match(r"^/r/\w+/s/\w+", path):
            resolved = self._resolve_reddit_share(url)
            return self.normalize_url(resolved)  # recurse with the real URL

        # ── 3 & 4. Comment or post page ──────────────────────────────────────
        post_match = re.match(r"^/r/\w+/comments/(\w+)", path)
        if post_match and "reddit.com" in netloc:
            post_id = post_match.group(1)
            comment_match = re.search(r"/comment/(\w+)", path)
            comment_id = comment_match.group(1) if comment_match else None
            media_url = self._extract_media_from_post(post_id, comment_id)
            return self.normalize_url(media_url)  # recurse: might be preview or v.redd.it

        # ── 5. reddit.com/media?url=<encoded preview URL> ────────────────────
        if path == "/media" and "reddit.com" in netloc:
            inner = parse_qs(parsed.query).get("url", [None])[0]
            if inner:
                return self.normalize_url(unquote(inner))  # recurse with unwrapped URL

        # ── 6. preview.redd.it — ensure GIFs are served as mp4 ───────────────
        if "preview.redd.it" in netloc:
            return self._ensure_mp4(url)

        # ── 7. i.redd.it — direct static image, nothing to do ────────────────
        if "i.redd.it" in netloc:
            return url

        # Fallback: best-effort decode and return
        return unquote(url)


    def _resolve_reddit_share(self, share_url: str) -> str:
        """
        Follow a short share link (reddit.com/r/<sub>/s/<id>) to its canonical
        post URL without downloading the page body.
        """
        try:
            r = requests.head(
                share_url, headers=REDDIT_HEADERS,
                allow_redirects=True, timeout=10
            )
            return r.url  # final URL after all redirects
        except requests.RequestException as e:
            raise ValueError(f"Could not resolve Reddit share URL {share_url}: {e}")


    def _extract_media_from_post(self, post_id: str, comment_id: str | None = None) -> str:
        """
        Hit the Reddit JSON API for a post and return its best media URL.

        For comment links the comment_id is passed but the media always lives
        on the parent post, so we only need the post JSON.
        """
        api_url = f"https://www.reddit.com/comments/{post_id}.json?limit=1&raw_json=1"
        try:
            r = requests.get(api_url, headers=REDDIT_HEADERS, timeout=10)
            r.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Reddit API request failed for post {post_id}: {e}")

        try:
            post_data = r.json()[0]["data"]["children"][0]["data"]
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected Reddit API response structure: {e}")

        # Priority 1 – native Reddit video (v.redd.it)
        if post_data.get("is_video"):
            return post_data["url"]  # normalize_url will route this to yt-dlp

        # Priority 2 – preview GIF/MP4 variants
        try:
            variants = (
                post_data["preview"]["images"][0]["variants"]
            )
            # prefer the explicit mp4 variant; fall back to gif source
            if "mp4" in variants:
                return variants["mp4"]["source"]["url"]
            if "gif" in variants:
                return variants["gif"]["source"]["url"]
        except (KeyError, IndexError):
            pass

        # Priority 3 – plain post URL (might be a preview.redd.it or i.redd.it link)
        post_url = post_data.get("url", "")
        if post_url:
            return post_url

        raise ValueError(f"No downloadable media found in post {post_id}")


    def _ensure_mp4(self, url: str) -> str:
        """For preview.redd.it GIF URLs, rewrite to request mp4 delivery."""
        base = url.split("?")[0]
        if base.endswith(".gif") and "format=mp4" not in url:
            # Strip old query string; the 's' signature becomes invalid anyway
            # when params change, so drop it. Reddit serves unsigned mp4 previews.
            return base + "?format=mp4"
        return url

    def get_extension(self, url: str) -> str:
        """Infer the extension from the url and format settings."""
        if 'format=mp4' in url:
            return 'mp4'
        if url.endswith('.gif'):
            return 'gif'
        if url.endswith('.jpg') or url.endswith('.jpeg'):
            return 'jpg'
        if url.endswith('.png'):
            return 'png'
        return self.format

    def download_file(self, url: str, output_file: str):
        """Download a file from a URL into a filename.

        :param str url: URL of the file
        :param str output_file: Name of the output file
        """
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True, colour="red")

        with open(output_file, "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()
        log(f"Downloaded {output_file} from {url}", "INFO")