"""
Terminal display: banner and colored lyrics output.
"""

from lyricsfetch.utils import Colors
from lyricsfetch.fetcher import fetch_lyrics
from lyricsfetch.storage import save_lyrics


def print_banner():
    """Print the splash banner on startup."""
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════╗
║     {Colors.YELLOW}🎵 LyricsFetch v1.0{Colors.CYAN}            ║
║  {Colors.DIM}Paste. Play. Read.{Colors.CYAN}               ║
╚══════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def display_lyrics(metadata: dict, lyrics: str, provider: str):
    """Print lyrics nicely formatted to terminal."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}╔══ {'🎵':^3} ═══════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.RESET}  {Colors.YELLOW}{metadata['track']:46s}{Colors.RESET}  {Colors.BOLD}{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.RESET}  {Colors.MAGENTA}{metadata['artist']:46s}{Colors.RESET}  {Colors.BOLD}{Colors.CYAN}║{Colors.RESET}")
    if metadata.get("duration"):
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.RESET}  {Colors.DIM}⏱ {metadata['duration']:44s}{Colors.RESET}  {Colors.BOLD}{Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚══════════════════════════════════════╝{Colors.RESET}")

    print(f"\n  {Colors.DIM}─── lyrics via {provider} ───{Colors.RESET}\n")

    for line in lyrics.split("\n"):
        line = line.strip()
        if not line:
            print()
        elif line.isupper() or line.endswith(":"):
            print(f"{Colors.BOLD}{Colors.GREEN}{line}{Colors.RESET}")
        elif line.startswith("["):
            print(f"{Colors.BOLD}{Colors.YELLOW}{line}{Colors.RESET}")
        else:
            print(f"  {line}")

    print()


def search_manual():
    """Interactive mode: input artist and song manually."""
    print(f"\n{Colors.CYAN}📝 Manual lyrics search{Colors.RESET}")
    artist = input(f"  {Colors.BOLD}Artist:{Colors.RESET} ").strip()
    song = input(f"  {Colors.BOLD}Song:{Colors.RESET} ").strip()

    if not artist or not song:
        print(f"{Colors.RED}Both artist and song are required.{Colors.RESET}")
        return

    lyrics, provider = fetch_lyrics(artist, song)
    if lyrics:
        metadata = {"artist": artist, "track": song, "duration": None}
        display_lyrics(metadata, lyrics, provider)
        save = input(f"  {Colors.DIM}Save to file? (y/n):{Colors.RESET} ").strip().lower()
        if save == "y":
            path = save_lyrics(artist, song, lyrics)
            print(f"  {Colors.GREEN}✅ Saved: {path}{Colors.RESET}")
    else:
        print(f"\n  {Colors.RED}❌ {provider}{Colors.RESET}")
        print(f"  {Colors.DIM}Try a different spelling or check the artist/song name.{Colors.RESET}")
