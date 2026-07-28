"""
Utility functions: colored output, duration formatting, YouTube URL handling.
"""

import re
from urllib.parse import urlparse, parse_qs


class Colors:
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    MAGENTA = "\033[95m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def format_duration(seconds: int) -> str:
    """Format seconds into human-readable duration string."""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def is_valid_youtube_url(url: str) -> bool:
    """Check if URL is a valid YouTube link."""
    patterns = [
        r"^https?://(www\.)?youtube\.com/watch\?v=",
        r"^https?://youtu\.be/",
        r"^https?://(www\.)?youtube\.com/shorts/",
        r"^https?://(www\.)?youtube\.com/embed/",
        r"^https?://(m\.)?youtube\.com/watch\?v=",
        r"^https?://music\.youtube\.com/watch\?v=",
    ]
    return any(re.match(p, url) for p in patterns)


def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats."""
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/").split("?")[0]
    query = parse_qs(parsed.query)
    return query.get("v", [None])[0]
