"""
File I/O for saving lyrics to disk.
"""

import os
import re


def save_lyrics(artist: str, song: str, lyrics: str, output_dir: str | None = None) -> str:
    """Save lyrics to a text file. Returns the file path."""
    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "lyrics",
        )

    os.makedirs(output_dir, exist_ok=True)

    safe_artist = re.sub(r"[^\w\s-]", "", artist).strip().replace(" ", "_")[:40]
    safe_song = re.sub(r"[^\w\s-]", "", song).strip().replace(" ", "_")[:60]
    filename = f"{safe_artist}__{safe_song}.txt"
    filepath = os.path.join(output_dir, filename)

    counter = 1
    while os.path.exists(filepath):
        name, ext = os.path.splitext(filename)
        filepath = os.path.join(output_dir, f"{name}_{counter}{ext}")
        counter += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"{song} — {artist}\n")
        f.write("=" * 50 + "\n\n")
        f.write(lyrics)
        f.write("\n")

    return filepath
