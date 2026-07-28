# YouTube Music TUI

TUI (Terminal User Interface) untuk streaming musik dari YouTube tanpa API - music player lengkap di terminal.

[English](README.md) | **Bahasa Indonesia**

## Fitur

### Inti
- Pencarian YouTube - Scraping hasil pencarian (tanpa API key)
- Audio Streaming - Play via mpv (yt-dlp)
- Lirik Sinkron - Multi-provider dengan highlighting real-time (lrclib.net + 3 fallback)
- Kontrol Player Lengkap - Play/pause, stop, next/prev

### Playlist & Library
- Import Playlist YouTube - Paste URL playlist untuk auto-fetch semua video
- Manajemen Playlist - Tambah, hapus, atur ulang track
- Sistem Favorit - Bookmark lagu favorit
- Riwayat Playback - Lacak apa yang sudah diputar
- Mode Shuffle - Pemutaran acak
- Mode Repeat - None, one, all

### Advanced
- Download/Cache - Dukungan playback offline
- Kontrol Volume - Slider interaktif dengan kontrol real-time
- Timing Lirik - Sesuaikan offset sinkronisasi untuk intro/dialog
- Auto-play Next - Sistem antrian dengan auto-advance
- Multiple Views - Search, playlist, history, favorites
- Persistent Storage - Simpan playlist, favorit, riwayat

## Requirements

- Python 3.8+
- ffmpeg (ekstraksi audio)
- mpv (audio playback)

## Instalasi

### Dari Source

```bash
# Clone atau navigasi ke direktori
cd youtube-music-tui

# Buat virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# atau: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install system dependencies
# Ubuntu/Debian:
sudo apt install ffmpeg mpv

# macOS:
brew install ffmpeg mpv

# Windows:
# Download dari ffmpeg.org dan mpv.io
```

### Build Binary

Build executable standalone dengan PyInstaller:

```bash
# Linux/macOS:
./build.sh

# Windows:
build.bat

# Manual build:
pyinstaller youtube-music-tui.spec
```

Binary akan ada di direktori `dist/`.

### Download Binary Pre-built

Download binary pre-built dari [Releases](https://github.com/yourusername/youtube-music-tui/releases):
- Linux: `youtube-music-tui-linux-amd64`
- macOS: `youtube-music-tui-macos-amd64`
- Windows: `youtube-music-tui-windows-amd64.exe`

Catatan: Anda tetap perlu install `ffmpeg` dan `mpv` sebagai system dependencies.

## Penggunaan

```bash
# Dari source:
source .venv/bin/activate
python main.py

# Dari binary:
./youtube-music-tui  # Linux/macOS
youtube-music-tui.exe  # Windows
```

## Keyboard Shortcuts

### Playback
- `Space` - Play/Pause
- `s` - Stop
- `n` - Track berikutnya
- `p` - Track sebelumnya

### Volume
- `v` - Buka volume slider
- (lalu `←` `→` untuk adjust, `m` untuk mute)

### Lirik
- `l` - Pencarian lirik manual
- `+` / `=` - Tunda lirik +0.5s
- `-` - Majukan lirik -0.5s

### Playlist
- `a` - Tambah hasil ke playlist
- `d` - Download/cache track
- `f` - Tambah ke favorit (toggle)
- `c` - Hapus playlist

### Mode
- `r` - Cycle repeat (none, one, all)
- `z` - Toggle shuffle

### Navigasi
- `/` - Focus search bar
- `Tab` - Switch focus
- `h` - Tampilkan help screen

### Views
- `1` - Tampilkan hasil pencarian
- `2` - Tampilkan playlist
- `3` - Tampilkan riwayat
- `4` - Tampilkan favorit

### Lainnya
- `q` - Keluar
- `Esc` - Tutup help/dialogs

## Layout

```
╔═══════════════════════════════════════════════════════════╗
║ Search: [Ketik di sini atau paste URL]                   ║
╠═════════════════════╦═════════════════════════════════════╣
║                     ║  Player                             ║
║  Lirik              ║  Judul - Artist                     ║
║  [Synced]           ║  Playing  00:45 / 03:20             ║
║  [Offset: +0.5s]    ║  ████████████░░░░░░░░ 45%          ║
║                     ║  [70%] ████████████░░░░░░░░ (V)     ║
║  ▶ Baris saat ini   ║  Repeat All  Shuffle                ║
║  Baris berikutnya   ╠═════════════════════════════════════╣
║  Baris ke depan...  ║  Hasil Pencarian (15)               ║
║                     ║  1. Judul Lagu - Artist             ║
║                     ║     Channel | 3:45                  ║
║                     ║  2. Lagu Lain                       ║
║                     ║  ...                                ║
╚═════════════════════╩═════════════════════════════════════╝
 q Quit │ space Play/Pause │ h Help │ / Search
```

## Struktur Proyek

```
youtube-music-tui/
├── main.py                 # Aplikasi TUI utama
├── youtube_scraper.py      # YouTube search + playlist scraper
├── audio_player.py         # mpv player wrapper dengan kontrol real-time
├── lyrics_fetcher.py       # Lyrics fetcher (lrclib.net + multi-provider)
├── playlist_manager.py     # Playlist/history/favorites manager
├── cache_manager.py        # Download/cache system
├── lyricsfetch/            # Modul fetching lyrics
│   ├── fetcher.py          # 4 provider API
│   ├── metadata.py         # Title parser
│   └── ...
├── .music_data/            # Data persisten (auto-created)
│   ├── playlist.json
│   ├── history.json
│   └── favorites.json
├── .music_cache/           # Track yang di-download (auto-created)
└── requirements.txt
```

## Tips Penggunaan

1. **Search** - Ketik nama artist/lagu atau paste URL YouTube
2. **Import Playlist** - Paste URL playlist YouTube (contoh: `https://youtube.com/playlist?list=...`)
3. **Buat Playlist Manual** - Tekan `a` pada hasil pencarian untuk menambah track
4. **Play Queue** - Tekan `2` untuk lihat playlist, klik untuk play
5. **Auto-play** - Track berikutnya otomatis diputar saat track saat ini selesai
6. **Mode Offline** - Tekan `d` untuk download/cache track untuk playback offline
7. **Favorit** - Tekan `f` untuk bookmark track, tekan `4` untuk lihat semua favorit
8. **Riwayat** - Tekan `3` untuk melihat riwayat playback
9. **Sinkronisasi Lirik** - Tekan `+`/`-` untuk menyesuaikan timing pada lagu dengan intro/dialog

## Tech Stack

- **yt-dlp** - YouTube downloader/extractor
- **textual** - Framework TUI modern
- **python-mpv** - Audio playback dengan kontrol real-time
- **requests** + **beautifulsoup4** - Web scraping
- **lrclib.net** - Lirik sinkron (format LRC)
- **lyricsfetch** - Multi-provider lyrics fallback (lyrics.ovh, textyl.co)

## Catatan

- Scraping YouTube mungkin gagal jika Google mengubah struktur HTML
- Lirik sinkron dari lrclib.net dengan dukungan penyesuaian timing
- Lirik plain fallback dari 4 provider
- Audio streaming langsung via mpv (tanpa download intermediate kecuali di-cache)
- Semua data disimpan di direktori `.music_data/`
- Cache disimpan di direktori `.music_cache/`

## Lisensi

MIT

## Kontribusi

Pull request welcome! Ide untuk improvement:
- Auto-scroll lirik yang lebih baik
- Equalizer/efek audio
- Remote control API
- Scrobbling (integrasi Last.fm)
- Dukungan seek yang lebih baik
- Audio visualizer

---

Dibuat dengan perhatian. Nikmati musikmu!
