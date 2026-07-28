"""
🎵 LyricsFetch — modular package for fetching song lyrics from YouTube links.
"""

from lyricsfetch.utils import (
    Colors,
    format_duration,
    is_valid_youtube_url,
    extract_video_id,
)
from lyricsfetch.metadata import extract_metadata, parse_title, clean_song_title
from lyricsfetch.fetcher import fetch_lyrics, generate_query_variations, LYRICS_PROVIDERS
from lyricsfetch.display import print_banner, display_lyrics, search_manual
from lyricsfetch.storage import save_lyrics

__all__ = [
    "Colors",
    "format_duration",
    "is_valid_youtube_url",
    "extract_video_id",
    "extract_metadata",
    "parse_title",
    "clean_song_title",
    "fetch_lyrics",
    "generate_query_variations",
    "LYRICS_PROVIDERS",
    "print_banner",
    "display_lyrics",
    "search_manual",
    "save_lyrics",
]
