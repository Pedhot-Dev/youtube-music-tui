"""
YouTube metadata extraction and title parsing via yt-dlp.
"""

import re
import sys

from lyricsfetch.utils import Colors, format_duration


def extract_metadata(youtube_url: str) -> dict:
    """Extract title, artist, and other metadata from a YouTube URL using yt-dlp."""
    try:
        import yt_dlp
    except ImportError:
        print("❌ yt-dlp not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
    }

    print(f"{Colors.DIM}🔍 Fetching video info...{Colors.RESET}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(youtube_url, download=False)
        except yt_dlp.utils.ExtractorError:
            print(f"{Colors.RED}❌ This video is age-restricted or unavailable (yt-dlp couldn't extract info).{Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Try --manual mode to enter artist/song directly.{Colors.RESET}")
            sys.exit(1)
        except yt_dlp.utils.DownloadError:
            print(f"{Colors.RED}❌ Network/connection issue while fetching video info.{Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Try --manual mode to enter artist/song directly.{Colors.RESET}")
            sys.exit(1)
        except Exception:
            print(f"{Colors.RED}❌ An unexpected error occurred while fetching video info.{Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Try --manual mode to enter artist/song directly.{Colors.RESET}")
            sys.exit(1)

    title = info.get("title", "Unknown Title")
    uploader = info.get("uploader", "")
    channel = info.get("channel", "")
    duration = info.get("duration", 0)
    webpage_url = info.get("webpage_url", youtube_url)
    thumbnail = info.get("thumbnail", "")

    # Try to get artist via various fields
    artist = None
    track = None

    if info.get("track"):
        track = info.get("track")
        artist = info.get("artist") or info.get("creator") or uploader

    if not artist or not track:
        parsed = parse_title(title, uploader)
        if parsed:
            artist = artist or parsed["artist"]
            track = track or parsed["track"]

    artist = artist or uploader or channel
    track = track or title

    # Clean artist name
    artist = re.sub(r"\s*VEVO\s*", "", artist, flags=re.IGNORECASE).strip()
    artist = re.sub(r"\s*-\s*Topic\s*", "", artist, flags=re.IGNORECASE).strip()
    artist = re.sub(r"\s*Official\s*", "", artist, flags=re.IGNORECASE).strip()

    return {
        "title": title,
        "artist": artist,
        "track": track,
        "uploader": uploader,
        "channel": channel,
        "duration": format_duration(duration),
        "url": webpage_url,
        "thumbnail": thumbnail,
    }


def parse_title(title: str, uploader: str = "") -> dict | None:
    """
    Try to extract artist & song from title using common patterns:
    - "Artist - Song"
    - "Artist – Song" (en-dash)
    - "ft.", "feat." patterns
    """
    patterns = [
        r"^(.+?)\s*[–\-—]\s*(.+?)\s*(?:\(|\[|\||$)",
        r"^(.+?)\s*[–\-—]\s*(.+?)$",
    ]

    for pat in patterns:
        m = re.match(pat, title.strip())
        if m:
            artist_candidate = m.group(1).strip()
            song_candidate = m.group(2).strip()

            if not re.match(
                r"^(Mix|Remix|Live|Cover|Medley|Best|Top|Playlist)",
                artist_candidate,
                re.IGNORECASE,
            ):
                return {"artist": artist_candidate, "track": song_candidate}

    if uploader:
        return {"artist": uploader, "track": title}

    return None


def clean_song_title(title: str) -> str:
    """Clean up song title for better API matching."""
    title = re.sub(
        r"\([^)]*(?:audio|lyrics|video|official|music|4k|hd|hq|remaster|explicit|clean)[^)]*\)",
        "", title, flags=re.IGNORECASE
    )
    title = re.sub(r"\[[^\]]*\]", "", title)
    title = re.sub(r"\s+(ft|feat|featuring)[.\s].*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", title).strip()
    return title
