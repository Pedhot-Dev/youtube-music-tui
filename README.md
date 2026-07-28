# YouTube Music TUI

A Terminal User Interface (TUI) for streaming music from YouTube without API - fully featured music player.

## Features

### Core
- YouTube Search - Scrape search results (no API key required)
- Audio Streaming - Play via mpv (yt-dlp)
- Synced Lyrics - Multi-provider lyrics with live highlighting (lrclib.net + 3 fallbacks)
- Full Player Controls - Play/pause, stop, next/prev

### Playlist & Library
- YouTube Playlist Import - Paste playlist URL to auto-fetch all videos
- Playlist Management - Add, remove, reorder tracks
- Favorites System - Bookmark your favorite tracks
- Playback History - Track what you've played
- Shuffle Mode - Random playback
- Repeat Modes - None, one, all

### Advanced
- Download/Cache - Offline playback support
- Volume Control - Interactive slider with real-time control
- Lyrics Timing - Adjust sync offset for intro/dialog
- Auto-play Next - Queue system with auto-advance
- Multiple Views - Search, playlist, history, favorites
- Persistent Storage - Save playlists, favorites, history

## Requirements

- Python 3.8+
- ffmpeg (audio extraction)
- mpv (audio playback)

## Installation

### From Source

```bash
# Clone or navigate to directory
cd youtube-music-tui

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install system dependencies
# Ubuntu/Debian:
sudo apt install ffmpeg mpv

# macOS:
brew install ffmpeg mpv

# Windows:
# Download from ffmpeg.org and mpv.io
```

### Building Binary

Build standalone executable with PyInstaller:

```bash
# Linux/macOS:
./build.sh

# Windows:
build.bat

# Manual build:
pyinstaller youtube-music-tui.spec
```

Binary will be in `dist/` directory.

### Download Pre-built Binaries

Download pre-built binaries from [Releases](https://github.com/yourusername/youtube-music-tui/releases):
- Linux: `youtube-music-tui-linux-amd64`
- macOS: `youtube-music-tui-macos-amd64`
- Windows: `youtube-music-tui-windows-amd64.exe`

Note: You still need to install `ffmpeg` and `mpv` system dependencies.

## Usage

```bash
# From source:
source .venv/bin/activate
python main.py

# From binary:
./youtube-music-tui  # Linux/macOS
youtube-music-tui.exe  # Windows
```

## Keyboard Shortcuts

### Playback
- `Space` - Play/Pause
- `s` - Stop
- `n` - Next track
- `p` - Previous track

### Volume
- `v` - Open volume slider
- (then `←` `→` to adjust, `m` to mute)

### Lyrics
- `l` - Manual lyrics search
- `+` / `=` - Delay lyrics +0.5s
- `-` - Advance lyrics -0.5s

### Playlist
- `a` - Add current result to playlist
- `d` - Download/cache current track
- `f` - Add to favorites (toggle)
- `c` - Clear playlist

### Modes
- `r` - Cycle repeat (none, one, all)
- `z` - Toggle shuffle

### Navigation
- `/` - Focus search bar
- `Tab` - Switch focus
- `h` - Show help screen

### Views
- `1` - Show search results
- `2` - Show playlist
- `3` - Show history
- `4` - Show favorites

### Other
- `q` - Quit
- `Esc` - Close help/dialogs

## Layout

```
╔═══════════════════════════════════════════════════════════╗
║ Search: [Type here or paste URL]                         ║
╠═════════════════════╦═════════════════════════════════════╣
║                     ║  Player                             ║
║  Lyrics             ║  Title - Artist                     ║
║  [Synced]           ║  Playing  00:45 / 03:20             ║
║  [Offset: +0.5s]    ║  ████████████░░░░░░░░ 45%          ║
║                     ║  [70%] ████████████░░░░░░░░ (V)     ║
║  ▶ Current line     ║  Repeat All  Shuffle                ║
║  Next line          ╠═════════════════════════════════════╣
║  Future lines...    ║  Search Results (15)                ║
║                     ║  1. Song Title - Artist             ║
║                     ║     Channel | 3:45                  ║
║                     ║  2. Another Song                    ║
║                     ║  ...                                ║
╚═════════════════════╩═════════════════════════════════════╝
 q Quit │ space Play/Pause │ h Help │ / Search
```

## Project Structure

```
youtube-music-tui/
├── main.py                 # Main TUI application
├── youtube_scraper.py      # YouTube search + playlist scraper
├── audio_player.py         # mpv player wrapper with real-time control
├── lyrics_fetcher.py       # Lyrics fetcher (lrclib.net + multi-provider)
├── playlist_manager.py     # Playlist/history/favorites manager
├── cache_manager.py        # Download/cache system
├── lyricsfetch/            # Lyrics fetching module
│   ├── fetcher.py          # 4 provider APIs
│   ├── metadata.py         # Title parser
│   └── ...
├── .music_data/            # Persistent data (auto-created)
│   ├── playlist.json
│   ├── history.json
│   └── favorites.json
├── .music_cache/           # Downloaded tracks (auto-created)
└── requirements.txt
```

## Usage Tips

1. **Search** - Type artist/song name or paste YouTube URL
2. **Import Playlist** - Paste YouTube playlist URL (e.g., `https://youtube.com/playlist?list=...`)
3. **Build Manual Playlist** - Press `a` on search results to add tracks
4. **Play Queue** - Press `2` to view playlist, click to play
5. **Auto-play** - Next track plays automatically when current track ends
6. **Offline Mode** - Press `d` to download/cache tracks for offline playback
7. **Favorites** - Press `f` to bookmark tracks, press `4` to view all favorites
8. **History** - Press `3` to see playback history
9. **Lyrics Sync** - Press `+`/`-` to adjust timing for songs with intro/dialog

## Tech Stack

- **yt-dlp** - YouTube downloader/extractor
- **textual** - Modern TUI framework
- **python-mpv** - Audio playback with real-time control
- **requests** + **beautifulsoup4** - Web scraping
- **lrclib.net** - Synced lyrics (LRC format)
- **lyricsfetch** - Multi-provider lyrics fallback (lyrics.ovh, textyl.co)

## Notes

- YouTube scraping may break if Google changes HTML structure
- Synced lyrics from lrclib.net with timing adjustment support
- Plain lyrics fallback from 4 providers
- Audio streams directly via mpv (no intermediate download unless cached)
- All data persisted in `.music_data/` directory
- Cache stored in `.music_cache/` directory

## License

MIT

## Contributing

Pull requests welcome! Ideas for improvement:
- Better lyrics auto-scroll
- Equalizer/audio effects
- Remote control API
- Scrobbling (Last.fm integration)
- Better seek support
- Audio visualizer

---

Made with care. Enjoy your music!
