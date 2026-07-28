"""
Lyrics fetching with multi-provider fallback and query variation generation.
"""

import json
import re
import sys

try:
    import requests
except ImportError:
    print("❌ requests not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

from lyricsfetch.metadata import clean_song_title
from lyricsfetch.utils import Colors

LYRICS_PROVIDERS = [
    {
        "name": "lyrics.ovh",
        "url": "https://api.lyrics.ovh/v1/{artist}/{song}",
        "parse": lambda data: data.get("lyrics", ""),
    },
    {
        "name": "api.lyrist.xyz",
        "url": "https://api.lyrist.xyz/{artist}/{song}",
        "parse": lambda data: data.get("lyrics", ""),
    },
    {
        "name": "textyl.co",
        "url": "https://api.textyl.co/api/lyrics?q={artist}%20{song}",
        "parse": lambda data: (
            data.get("lyrics", "")
            if isinstance(data, dict)
            else (data[0].get("lyrics", "") if isinstance(data, list) and len(data) > 0 else "")
        ),
    },
    {
        "name": "weeb-api",
        "url": "https://weeb-api.vercel.app/lyrics?artist={artist}&title={song}",
        "parse": lambda data: (
            data.get("lyrics", "")
            if isinstance(data, dict)
            else (data[0].get("lyrics", "") if isinstance(data, list) and len(data) > 0 else "")
        ),
    },
]


def generate_query_variations(artist: str, song: str) -> list[tuple[str, str]]:
    """Generate variations of artist/song to try for broader matching."""
    variations = []
    variations.append((artist, song))

    song_clean = clean_song_title(song)
    if song_clean != song:
        variations.append((artist, song_clean))

    artist_clean = re.sub(
        r"\s+(ft|feat|featuring)[.\s].*$", "", artist, flags=re.IGNORECASE
    ).strip()
    if artist_clean != artist:
        variations.append((artist_clean, song))
        variations.append((artist_clean, song_clean))

    return variations


def fetch_lyrics(artist: str, song: str) -> tuple[str | None, str]:
    """
    Fetch lyrics from multiple providers.
    Returns (lyrics_text, provider_name) or (None, error_msg).
    """
    query_variations = generate_query_variations(artist, song)
    print(f"{Colors.DIM}  🎤 Artist: {artist}{Colors.RESET}")
    print(f"{Colors.DIM}  🎵 Song:   {song}{Colors.RESET}")

    for artist_try, song_try in query_variations:
        artist_clean = re.sub(r"[\(\)\[\]]", "", artist_try).strip()
        song_clean = re.sub(r"[\(\)\[\]]", "", song_try).strip()

        if (artist_clean, song_clean) != (artist, song):
            print(f"{Colors.DIM}  🔄 Trying: {artist_clean} — {song_clean}{Colors.RESET}")
        else:
            print(f"{Colors.DIM}  🔍 Searching...{Colors.RESET}")

        for provider in LYRICS_PROVIDERS:
            url = provider["url"].format(
                artist=requests.utils.quote(artist_clean),
                song=requests.utils.quote(song_clean),
            )

            try:
                print(f"\r  {Colors.DIM}⏳ Searching {provider['name']}...{Colors.RESET}", end="", flush=True)
                resp = requests.get(url, timeout=10, headers={
                    "User-Agent": "LyricsFetch/1.0",
                    "Accept": "application/json",
                })
                print("\r" + " " * 60 + "\r", end="", flush=True)

                if resp.status_code == 200:
                    data = resp.json()
                    lyrics = provider["parse"](data)
                    if lyrics and lyrics.strip():
                        return lyrics.strip(), provider["name"]

                elif resp.status_code == 404:
                    continue

            except requests.exceptions.Timeout:
                print("\r" + " " * 60 + "\r", end="", flush=True)
                continue
            except requests.exceptions.ConnectionError:
                print("\r" + " " * 60 + "\r", end="", flush=True)
                continue
            except json.JSONDecodeError:
                print("\r" + " " * 60 + "\r", end="", flush=True)
                continue

    return None, "No lyrics found on any provider."
