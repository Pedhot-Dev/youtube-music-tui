#!/usr/bin/env python3
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Input, Static, ListView, ListItem, Label, ProgressBar, Button
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import Screen, ModalScreen
import asyncio
from threading import Thread
import os

from youtube_scraper import YouTubeScraper
from audio_player import AudioPlayer
from lyrics_fetcher import LyricsFetcher
from playlist_manager import PlaylistManager
from cache_manager import CacheManager


class VolumeSliderScreen(ModalScreen):
    """Modal screen for volume control with slider"""
    
    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("left", "volume_down", "Volume -"),
        ("right", "volume_up", "Volume +"),
        ("m", "toggle_mute", "Mute"),
    ]
    
    def __init__(self, player, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = player
        self.volume = player.volume
        self.muted = player.is_muted()
    
    def compose(self) -> ComposeResult:
        with Container(id="volume-container"):
            yield Static("🔊 Volume Control", id="volume-title")
            yield Static("", id="volume-slider")
            yield Static("Use ← → to adjust | M to mute | ESC to close", id="volume-help")
    
    def on_mount(self):
        self.update_display()
    
    def update_display(self):
        slider = self.query_one("#volume-slider", Static)
        
        if self.muted:
            slider.update("[red]🔇 MUTED[/]")
        else:
            vol_percent = int(self.volume * 100)
            filled = int(self.volume * 40)  # Bigger slider
            bar = "█" * filled + "░" * (40 - filled)
            icon = "🔊" if vol_percent > 66 else "🔉" if vol_percent > 33 else "🔈"
            slider.update(f"{icon} [{vol_percent:3d}%]\n{bar}")
    
    def action_volume_up(self):
        if not self.muted:
            self.volume = min(1.0, self.volume + 0.05)  # 5% steps
            self.player.set_volume(self.volume)
            self.update_display()
    
    def action_volume_down(self):
        if not self.muted:
            self.volume = max(0.0, self.volume - 0.05)  # 5% steps
            self.player.set_volume(self.volume)
            self.update_display()
    
    def action_toggle_mute(self):
        if self.muted:
            self.player.unmute()
            self.muted = False
        else:
            self.player.mute()
            self.muted = True
        self.update_display()


class LyricsSearchScreen(ModalScreen):
    """Manual lyrics search screen"""
    
    BINDINGS = [("escape", "dismiss", "Close")]
    
    def __init__(self, lyrics_fetcher, lyrics_panel, current_track=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lyrics_fetcher = lyrics_fetcher
        self.lyrics_panel = lyrics_panel
        self.current_track = current_track
    
    def compose(self) -> ComposeResult:
        with Container(id="lyrics-search-container"):
            yield Static("🔍 Manual Lyrics Search", id="lyrics-search-title")
            yield Input(placeholder="Artist name", id="artist-input")
            yield Input(placeholder="Track name", id="track-input")
            yield Input(placeholder="Album name (optional)", id="album-input")
            yield Input(placeholder="Duration in seconds (optional)", id="duration-input")
            yield Static("[dim]Press Enter on any field to search | ESC to cancel[/]", id="lyrics-search-help")
            yield Static("", id="lyrics-search-status")
    
    def on_mount(self):
        # Auto-fill from current track if available
        if self.current_track:
            title = self.current_track.get('title', '')
            
            # Try to parse artist/track from title
            if ' - ' in title:
                parts = title.split(' - ', 1)
                artist_input = self.query_one("#artist-input", Input)
                track_input = self.query_one("#track-input", Input)
                artist_input.value = parts[0].strip()
                track_input.value = parts[1].strip()
            else:
                track_input = self.query_one("#track-input", Input)
                track_input.value = title
        
        # Focus first input
        self.query_one("#artist-input", Input).focus()
    
    async def on_input_submitted(self, event: Input.Submitted):
        """Search when any input submitted"""
        await self.search_lyrics()
    
    async def search_lyrics(self):
        """Perform lyrics search"""
        artist_input = self.query_one("#artist-input", Input)
        track_input = self.query_one("#track-input", Input)
        album_input = self.query_one("#album-input", Input)
        duration_input = self.query_one("#duration-input", Input)
        status = self.query_one("#lyrics-search-status", Static)
        
        artist = artist_input.value.strip()
        track = track_input.value.strip()
        album = album_input.value.strip()
        duration_str = duration_input.value.strip()
        
        if not track:
            status.update("[yellow]⚠️ Please enter track name[/]")
            return
        
        # Parse duration
        duration = 0
        if duration_str:
            try:
                duration = int(duration_str)
            except:
                pass
        
        status.update("[cyan]🔍 Searching...[/]")
        
        # Fetch lyrics in background
        loop = asyncio.get_event_loop()
        lyrics_data = await loop.run_in_executor(
            None,
            self.lyrics_fetcher.fetch_lyrics,
            track,
            artist,
            album,
            duration
        )
        
        if lyrics_data and lyrics_data.get('text') and 'not found' not in lyrics_data.get('text', '').lower():
            provider = lyrics_data.get('provider', 'unknown')
            status.update(f"[green]✅ Found from {provider}! Closing...[/]")
            
            # Update lyrics panel
            self.lyrics_panel.set_lyrics(lyrics_data)
            
            # Auto-close after brief delay
            await asyncio.sleep(1)
            self.dismiss()
        else:
            status.update("[red]❌ Lyrics not found. Try different query.[/]")


class HelpScreen(Screen):
    """Help screen with keyboard shortcuts"""
    
    BINDINGS = [("escape", "dismiss", "Close")]
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("""
[bold cyan]Keyboard Shortcuts[/]

[yellow]Playback:[/]
  Space     - Play/Pause
  s         - Stop
  n         - Next track
  p         - Previous track
  
[yellow]Volume:[/]
  v         - Open volume slider
  (then ← → to adjust, m to mute)
  
[yellow]Lyrics:[/]
  l         - Manual lyrics search
  +/=       - Delay lyrics +0.5s
  -         - Delay lyrics -0.5s
  
[yellow]Playlist:[/]
  a         - Add current result to playlist
  d         - Download/cache current track
  f         - Add to favorites
  c         - Clear playlist
  
[yellow]Modes:[/]
  r         - Cycle repeat (none/one/all)
  z         - Toggle shuffle
  
[yellow]Navigation:[/]
  /         - Focus search
  tab       - Switch focus
  h         - Show this help
  
[yellow]Views:[/]
  1         - Show search results
  2         - Show playlist
  3         - Show history
  4         - Show favorites
  
[yellow]Other:[/]
  q         - Quit

[dim]Press ESC to close[/]
            """, id="help-text"),
            id="help-container"
        )


class VolumeBar(Static):
    """Visual volume bar"""
    
    volume = reactive(0.7)
    muted = reactive(False)
    
    def watch_volume(self, vol: float):
        self.update_bar()
    
    def watch_muted(self, muted: bool):
        self.update_bar()
    
    def update_bar(self):
        if self.muted:
            self.update("[red]🔇 MUTED[/] [dim](press V)[/]")
        else:
            vol_percent = int(self.volume * 100)
            filled = int(self.volume * 20)
            bar = "█" * filled + "░" * (20 - filled)
            icon = "🔊" if vol_percent > 66 else "🔉" if vol_percent > 33 else "🔈"
            self.update(f"{icon} [{vol_percent:3d}%] {bar} [dim](V)[/]")
    
    def on_mount(self):
        self.update_bar()


class LyricsPanel(ScrollableContainer):
    """Lyrics display panel with scrolling and synced lyrics support"""
    
    lyrics_text = reactive("")
    current_position = reactive(0.0)
    timing_offset = reactive(0.0)  # Offset in seconds
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "♪ Lyrics"
        self._label = None
        self.synced_lyrics = None  # List of (timestamp, line)
        self.plain_lyrics = ""
    
    def compose(self) -> ComposeResult:
        yield Static("[dim]No lyrics loaded[/]", id="lyrics-content")
    
    def on_mount(self):
        self._label = self.query_one("#lyrics-content", Static)
    
    def set_lyrics(self, lyrics_data: dict):
        """Set lyrics with synced support"""
        self.synced_lyrics = lyrics_data.get('synced')
        self.plain_lyrics = lyrics_data.get('text', '')
        self.timing_offset = 0.0  # Reset offset for new lyrics
        
        provider = lyrics_data.get('provider', 'unknown')
        metadata = lyrics_data.get('metadata', {})
        
        if self.synced_lyrics:
            self.border_title = f"♪ Lyrics [Synced - {provider}] [Offset: 0.0s]"
            # Display plain lyrics initially, will be highlighted on position update
            self._update_synced_display(0.0)
        else:
            self.border_title = f"♪ Lyrics [{provider}]"
            if metadata:
                artist = metadata.get('artist', '')
                track = metadata.get('track', '')
                header = f"[bold]{artist} - {track}[/]\n[dim]{provider}[/]\n\n" if artist and track else f"[dim]{provider}[/]\n\n"
                self.lyrics_text = header + self.plain_lyrics
            else:
                self.lyrics_text = f"[dim]{provider}[/]\n\n{self.plain_lyrics}"
    
    def adjust_timing(self, delta: float):
        """Adjust timing offset by delta seconds"""
        if not self.synced_lyrics:
            return
        
        self.timing_offset += delta
        # Update border to show offset
        provider = "synced"
        self.border_title = f"♪ Lyrics [Synced] [Offset: {self.timing_offset:+.1f}s]"
        
        # Re-render with new offset
        self._update_synced_display(self.current_position)
    
    def watch_lyrics_text(self, new_text: str):
        if self._label and not self.synced_lyrics:
            self._label.update(new_text if new_text else "[dim]No lyrics loaded[/]")
            self.scroll_home(animate=False)
    
    def watch_current_position(self, position: float):
        """Update highlighted line based on playback position"""
        if self.synced_lyrics and self._label:
            self._update_synced_display(position)
    
    def _update_synced_display(self, position: float):
        """Update lyrics display with current line highlighted"""
        if not self.synced_lyrics:
            return
        
        # Apply timing offset
        adjusted_position = position + self.timing_offset
        
        # Find current line index
        current_idx = -1
        for i, (timestamp, _) in enumerate(self.synced_lyrics):
            if adjusted_position >= timestamp:
                current_idx = i
            else:
                break
        
        # Build display with highlighting
        lines = []
        for i, (timestamp, text) in enumerate(self.synced_lyrics):
            if i == current_idx:
                # Highlight current line
                lines.append(f"[bold yellow on blue]▶ {text}[/]")
            elif i == current_idx + 1:
                # Next line slightly dimmed
                lines.append(f"[dim white]{text}[/]")
            elif i < current_idx:
                # Past lines very dim
                lines.append(f"[dim]{text}[/]")
            else:
                # Future lines normal
                lines.append(f"{text}")
        
        display_text = "\n".join(lines)
        self._label.update(display_text if display_text else "[dim]No lyrics[/]")
        
        # Auto-scroll to keep current line centered
        if current_idx >= 0:
            # Calculate scroll position to center current line
            # Each line is roughly 1 unit of height
            total_lines = len(self.synced_lyrics)
            
            # Get viewport height (approximate)
            viewport_height = self.size.height if hasattr(self, 'size') else 20
            
            # Target: put current line at 1/3 from top (not exact center, better UX)
            scroll_target = max(0, current_idx - int(viewport_height * 0.3))
            
            # Smooth scroll to target position
            try:
                # Scroll by line (approximate)
                self.scroll_to(y=scroll_target, animate=True, duration=0.3)
            except:
                pass


class PlayerPanel(Static):
    """Player info and controls"""
    
    current_title = reactive("")
    is_playing = reactive(False)
    is_paused = reactive(False)
    position = reactive(0.0)
    duration = reactive(0.0)
    repeat_mode = reactive("none")
    shuffle_mode = reactive(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "▶ Player"
    
    def compose(self) -> ComposeResult:
        yield Label("[dim]No track loaded[/]", id="track-title")
        yield Label("⏹ Stopped", id="player-status")
        yield Label("00:00 / 00:00", id="time-display")
        yield ProgressBar(total=100, show_eta=False, id="progress-bar")
        yield VolumeBar(id="volume-bar")
        yield Label("", id="mode-display")
    
    def on_mount(self):
        self.update_display()
    
    def watch_current_title(self, title: str):
        self.update_display()
    
    def watch_is_playing(self, playing: bool):
        self.update_display()
    
    def watch_is_paused(self, paused: bool):
        self.update_display()
    
    def watch_position(self, pos: float):
        self.update_display()
    
    def watch_repeat_mode(self, mode: str):
        self.update_display()
    
    def watch_shuffle_mode(self, shuffle: bool):
        self.update_display()
    
    def update_display(self):
        """Update all player display elements"""
        try:
            title_label = self.query_one("#track-title", Label)
            status_label = self.query_one("#player-status", Label)
            time_label = self.query_one("#time-display", Label)
            progress = self.query_one("#progress-bar", ProgressBar)
            mode_label = self.query_one("#mode-display", Label)
            
            # Title
            if self.current_title:
                title_label.update(f"[bold]{self.current_title}[/]")
            else:
                title_label.update("[dim]No track loaded[/]")
            
            # Status
            if self.is_playing:
                if self.is_paused:
                    status_label.update("⏸ [yellow]Paused[/]")
                else:
                    status_label.update("▶ [green]Playing[/]")
            else:
                status_label.update("⏹ [dim]Stopped[/]")
            
            # Time
            pos_str = self._format_time(self.position)
            dur_str = self._format_time(self.duration)
            time_label.update(f"{pos_str} / {dur_str}")
            
            # Progress
            if self.duration > 0:
                progress.update(total=int(self.duration), progress=int(self.position))
            
            # Modes
            modes = []
            if self.repeat_mode == "one":
                modes.append("[cyan]🔂 Repeat One[/]")
            elif self.repeat_mode == "all":
                modes.append("[cyan]🔁 Repeat All[/]")
            
            if self.shuffle_mode:
                modes.append("[magenta]🔀 Shuffle[/]")
            
            mode_label.update(" ".join(modes) if modes else "")
        except:
            pass
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds to MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"


class PlaylistView(ListView):
    """Playlist/Results view with mode switching"""
    pass


class YouTubeMusicTUI(App):
    """YouTube Music TUI Application - Full Featured"""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #search-container {
        height: 3;
        dock: top;
    }
    
    #main-container {
        layout: horizontal;
        height: 1fr;
    }
    
    #left-panel {
        width: 40%;
        border: solid green;
    }
    
    #right-panel {
        width: 60%;
        layout: vertical;
    }
    
    #player-panel {
        height: 15;
        border: solid blue;
        padding: 1;
    }
    
    #list-panel {
        height: 1fr;
        border: solid yellow;
    }
    
    PlaylistView {
        height: 1fr;
    }
    
    LyricsPanel {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }
    
    VolumeBar {
        height: 1;
        content-align: center middle;
    }
    
    #help-container {
        align: center middle;
        width: 60;
        height: auto;
        border: solid cyan;
        background: $surface;
        padding: 2;
    }
    
    #help-text {
        width: 100%;
        height: auto;
    }
    
    #volume-container {
        align: center middle;
        width: 60;
        height: 10;
        border: solid magenta;
        background: $surface;
        padding: 2;
    }
    
    #volume-title {
        text-align: center;
        text-style: bold;
    }
    
    #volume-slider {
        height: 3;
        content-align: center middle;
        text-align: center;
    }
    
    #volume-help {
        text-align: center;
        color: $text-muted;
    }
    
    #lyrics-search-container {
        align: center middle;
        width: 70;
        height: auto;
        border: solid yellow;
        background: $surface;
        padding: 2;
    }
    
    #lyrics-search-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #lyrics-search-container Input {
        margin-bottom: 1;
    }
    
    #lyrics-search-help {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    
    #lyrics-search-status {
        text-align: center;
        margin-top: 1;
        height: 2;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("space", "toggle_pause", "Play/Pause"),
        Binding("s", "stop", "Stop"),
        Binding("n", "next_track", "Next"),
        Binding("p", "previous_track", "Previous"),
        Binding("l", "search_lyrics", "Search Lyrics"),
        Binding("v", "open_volume", "Volume"),
        Binding("plus,equals", "lyrics_delay_increase", "Lyrics +0.5s"),
        Binding("minus", "lyrics_delay_decrease", "Lyrics -0.5s"),
        Binding("/", "focus_search", "Search"),
        Binding("a", "add_to_playlist", "Add to Playlist"),
        Binding("d", "download_track", "Download"),
        Binding("f", "toggle_favorite", "Favorite"),
        Binding("c", "clear_playlist", "Clear Playlist"),
        Binding("r", "cycle_repeat", "Repeat"),
        Binding("z", "toggle_shuffle", "Shuffle"),
        Binding("h", "show_help", "Help"),
        Binding("1", "show_search", "Search Results"),
        Binding("2", "show_playlist", "Playlist"),
        Binding("3", "show_history", "History"),
        Binding("4", "show_favorites", "Favorites"),
    ]
    
    def __init__(self):
        super().__init__()
        self.scraper = YouTubeScraper()
        self.player = AudioPlayer()
        self.lyrics_fetcher = LyricsFetcher()
        self.playlist_manager = PlaylistManager()
        self.cache_manager = CacheManager()
        
        self.search_results = []
        self.current_view = "search"  # search, playlist, history, favorites
        self.current_track = None
        
        self.player.on_position_update = self.on_player_position_update
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(id="search-container"):
            yield Input(placeholder="🔍 Search YouTube or paste URL...", id="search-input")
        
        with Horizontal(id="main-container"):
            # Left panel - Lyrics
            with Vertical(id="left-panel"):
                yield LyricsPanel(id="lyrics-panel")
            
            # Right panel - Player + List
            with Vertical(id="right-panel"):
                yield PlayerPanel(id="player-panel")
                with Container(id="list-panel"):
                    yield PlaylistView(id="playlist-view")
        
        yield Footer()
    
    def on_mount(self):
        """Initial setup"""
        self.title = "YouTube Music TUI"
        self.query_one("#search-input", Input).focus()
        self.update_view()
    
    async def on_input_submitted(self, event: Input.Submitted):
        """Handle search input"""
        query = event.value.strip()
        if not query:
            return
        
        # Clear input
        event.input.value = ""
        
        # Check if it's a URL
        if query.startswith("http"):
            # Check if it's a playlist URL
            if self.scraper.is_playlist_url(query):
                await self.fetch_and_load_playlist(query)
            else:
                await self.play_url(query)
        else:
            await self.search_and_display(query)
    
    async def search_and_display(self, query: str):
        """Search and display results"""
        self.notify(f"🔍 Searching: {query}")
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, self.scraper.search, query, 30)
        
        self.search_results = results
        self.current_view = "search"
        self.update_view()
        
        if not results:
            self.notify("❌ No results found", severity="warning")
        else:
            self.notify(f"✅ Found {len(results)} results")
    
    async def fetch_and_load_playlist(self, playlist_url: str):
        """Fetch playlist and add all videos to queue"""
        self.notify(f"📋 Fetching playlist...")
        
        loop = asyncio.get_event_loop()
        videos = await loop.run_in_executor(None, self.scraper.get_playlist_videos, playlist_url, 100)
        
        if not videos:
            self.notify("❌ Failed to fetch playlist", severity="error")
            return
        
        # Clear current playlist and add all videos
        self.playlist_manager.clear_playlist()
        for video in videos:
            self.playlist_manager.add_to_playlist(video)
        
        # Switch to playlist view
        self.current_view = "playlist"
        self.update_view()
        
        self.notify(f"✅ Loaded {len(videos)} videos from playlist")
        
        # Auto-play first track
        if videos:
            first_track = self.playlist_manager.play_track_at_index(0)
            if first_track:
                await self.play_track(first_track)
    
    def update_view(self):
        """Update list view based on current mode"""
        list_view = self.query_one("#playlist-view", PlaylistView)
        list_view.clear()
        
        # Update border title
        container = self.query_one("#list-panel", Container)
        
        if self.current_view == "search":
            container.border_title = "🔍 Search Results"
            items = self.search_results
            for i, item in enumerate(items):
                title = item.get('title', 'Unknown')
                channel = item.get('channel', '')
                duration = item.get('duration', '')
                label = f"{i+1}. {title}\n   [dim]{channel} | {duration}[/]"
                list_view.append(ListItem(Label(label)))
        
        elif self.current_view == "playlist":
            container.border_title = f"📋 Playlist ({len(self.playlist_manager.current_playlist)})"
            items = self.playlist_manager.current_playlist
            for i, item in enumerate(items):
                title = item.get('title', 'Unknown')
                marker = "▶" if i == self.playlist_manager.current_index else " "
                label = f"{marker} {i+1}. {title}"
                list_view.append(ListItem(Label(label)))
        
        elif self.current_view == "history":
            container.border_title = f"📜 History ({len(self.playlist_manager.history)})"
            items = self.playlist_manager.history[-50:][::-1]  # Last 50, reversed
            for i, item in enumerate(items):
                title = item.get('title', 'Unknown')
                played_at = item.get('played_at', '')[:16].replace('T', ' ')
                label = f"{i+1}. {title}\n   [dim]{played_at}[/]"
                list_view.append(ListItem(Label(label)))
        
        elif self.current_view == "favorites":
            container.border_title = f"⭐ Favorites ({len(self.playlist_manager.favorites)})"
            items = self.playlist_manager.favorites
            for i, item in enumerate(items):
                title = item.get('title', 'Unknown')
                label = f"{i+1}. {title}"
                list_view.append(ListItem(Label(label)))
    
    async def on_list_view_selected(self, event: PlaylistView.Selected):
        """Handle item selection"""
        idx = event.list_view.index
        if idx is None:
            return
        
        if self.current_view == "search":
            if idx < len(self.search_results):
                track = self.search_results[idx]
                await self.play_track(track)
        
        elif self.current_view == "playlist":
            track = self.playlist_manager.play_track_at_index(idx)
            if track:
                await self.play_track(track)
        
        elif self.current_view == "history":
            items = self.playlist_manager.history[-50:][::-1]
            if idx < len(items):
                track = items[idx]
                await self.play_track(track)
        
        elif self.current_view == "favorites":
            if idx < len(self.playlist_manager.favorites):
                track = self.playlist_manager.favorites[idx]
                await self.play_track(track)
    
    async def play_track(self, track: dict):
        """Play a track"""
        url = track.get('url', '')
        if not url:
            return
        
        self.current_track = track
        await self.play_url(url, track)
    
    async def play_url(self, url: str, track_info: dict = None):
        """Play video from URL"""
        self.notify(f"▶ Loading...")
        
        # Get video info if needed
        if not track_info:
            loop = asyncio.get_event_loop()
            video_info = await loop.run_in_executor(None, self.scraper.get_video_info, url)
            if video_info:
                track_info = video_info
            else:
                track_info = {'url': url, 'title': url}
        
        self.current_track = track_info
        
        # Add to history
        self.playlist_manager.add_to_history(track_info)
        
        # Update player panel
        player_panel = self.query_one("#player-panel", PlayerPanel)
        title = track_info.get('title', url)
        player_panel.current_title = title
        
        # Fetch lyrics in background
        lyrics_panel = self.query_one("#lyrics-panel", LyricsPanel)
        
        async def fetch_lyrics_async():
            loop = asyncio.get_event_loop()
            
            # Get duration for lrclib API
            duration = track_info.get('duration', 0)
            if not duration:
                # Wait a bit for player to get duration
                await asyncio.sleep(2)
                status = self.player.get_status()
                duration = int(status.get('duration', 0))
            
            lyrics_data = await loop.run_in_executor(
                None,
                self.lyrics_fetcher.fetch_lyrics_from_video_title,
                title,
                duration
            )
            lyrics_panel.set_lyrics(lyrics_data)
        
        asyncio.create_task(fetch_lyrics_async())
        
        # Check cache first
        cached_file = self.cache_manager.get_cached_file(url)
        
        # Play audio in thread
        def play_thread():
            if cached_file:
                self.notify("📦 Playing from cache")
                success = self.player.download_and_play(url)
            else:
                success = self.player.download_and_play(url)
            
            if not success:
                self.notify("❌ Failed to play", severity="error")
            else:
                # Auto-play next when finished
                self.call_later(self._check_and_play_next)
        
        Thread(target=play_thread, daemon=True).start()
        
        # Update player status
        player_panel.is_playing = True
        player_panel.is_paused = False
        
        # Update volume bar
        volume_bar = self.query_one("#volume-bar", VolumeBar)
        volume_bar.volume = self.player.volume
        volume_bar.muted = self.player.is_muted()
        
        # Get duration
        async def update_duration():
            await asyncio.sleep(2)
            status = self.player.get_status()
            player_panel.duration = status['duration']
        
        asyncio.create_task(update_duration())
    
    def _check_and_play_next(self):
        """Check if should play next track"""
        if not self.player.is_playing and self.playlist_manager.current_playlist:
            next_track = self.playlist_manager.get_next_track()
            if next_track:
                asyncio.create_task(self.play_track(next_track))
    
    def on_player_position_update(self, position: float):
        """Callback when player position updates"""
        try:
            player_panel = self.query_one("#player-panel", PlayerPanel)
            player_panel.position = position
            
            # Update lyrics panel with current position for synced lyrics
            lyrics_panel = self.query_one("#lyrics-panel", LyricsPanel)
            lyrics_panel.current_position = position
        except:
            pass
    
    # Actions
    def action_toggle_pause(self):
        if self.player.is_playing:
            self.player.toggle_pause()
            player_panel = self.query_one("#player-panel", PlayerPanel)
            player_panel.is_paused = self.player.is_paused
    
    def action_stop(self):
        self.player.stop()
        player_panel = self.query_one("#player-panel", PlayerPanel)
        player_panel.is_playing = False
        player_panel.is_paused = False
        player_panel.position = 0
    
    def action_next_track(self):
        next_track = self.playlist_manager.get_next_track()
        if next_track:
            asyncio.create_task(self.play_track(next_track))
            self.update_view()
        else:
            self.notify("No next track")
    
    def action_previous_track(self):
        prev_track = self.playlist_manager.get_previous_track()
        if prev_track:
            asyncio.create_task(self.play_track(prev_track))
            self.update_view()
        else:
            self.notify("No previous track")
    
    def action_open_volume(self):
        """Open volume slider screen"""
        self.push_screen(VolumeSliderScreen(self.player))
    
    def action_search_lyrics(self):
        """Open manual lyrics search screen"""
        lyrics_panel = self.query_one("#lyrics-panel", LyricsPanel)
        self.push_screen(LyricsSearchScreen(
            self.lyrics_fetcher, 
            lyrics_panel, 
            self.current_track
        ))
    
    def action_add_to_playlist(self):
        if self.current_view == "search":
            list_view = self.query_one("#playlist-view", PlaylistView)
            idx = list_view.index
            if idx is not None and idx < len(self.search_results):
                track = self.search_results[idx]
                self.playlist_manager.add_to_playlist(track)
                self.notify(f"➕ Added to playlist")
        elif self.current_track:
            self.playlist_manager.add_to_playlist(self.current_track)
            self.notify(f"➕ Added to playlist")
    
    def action_download_track(self):
        if self.current_track:
            url = self.current_track.get('url')
            title = self.current_track.get('title')
            if url:
                self.notify(f"📥 Downloading...")
                
                def download():
                    result = self.cache_manager.download_and_cache(url, title)
                    if result:
                        self.notify(f"✅ Downloaded!")
                    else:
                        self.notify(f"❌ Download failed", severity="error")
                
                Thread(target=download, daemon=True).start()
    
    def action_toggle_favorite(self):
        if self.current_track:
            is_fav = self.playlist_manager.is_favorite(self.current_track)
            if is_fav:
                self.playlist_manager.remove_from_favorites(self.current_track)
                self.notify("💔 Removed from favorites")
            else:
                self.playlist_manager.add_to_favorites(self.current_track)
                self.notify("⭐ Added to favorites")
            
            if self.current_view == "favorites":
                self.update_view()
    
    def action_clear_playlist(self):
        self.playlist_manager.clear_playlist()
        self.notify("🗑 Playlist cleared")
        if self.current_view == "playlist":
            self.update_view()
    
    def action_cycle_repeat(self):
        mode = self.playlist_manager.cycle_repeat()
        player_panel = self.query_one("#player-panel", PlayerPanel)
        player_panel.repeat_mode = mode
        
        icons = {"none": "➡", "one": "🔂", "all": "🔁"}
        self.notify(f"{icons[mode]} Repeat: {mode}")
    
    def action_toggle_shuffle(self):
        shuffle = self.playlist_manager.toggle_shuffle()
        player_panel = self.query_one("#player-panel", PlayerPanel)
        player_panel.shuffle_mode = shuffle
        self.notify(f"🔀 Shuffle: {'ON' if shuffle else 'OFF'}")
    
    def action_show_search(self):
        self.current_view = "search"
        self.update_view()
    
    def action_show_playlist(self):
        self.current_view = "playlist"
        self.update_view()
    
    def action_show_history(self):
        self.current_view = "history"
        self.update_view()
    
    def action_show_favorites(self):
        self.current_view = "favorites"
        self.update_view()
    
    def action_focus_search(self):
        self.query_one("#search-input", Input).focus()
    
    def action_show_help(self):
        self.push_screen(HelpScreen())
    
    def action_lyrics_delay_increase(self):
        """Increase lyrics timing offset by 0.5s"""
        lyrics_panel = self.query_one("#lyrics-panel", LyricsPanel)
        if lyrics_panel.synced_lyrics:
            lyrics_panel.adjust_timing(0.5)
            self.notify(f"⏱️ Lyrics offset: {lyrics_panel.timing_offset:+.1f}s")
        else:
            self.notify("⚠️ No synced lyrics loaded")
    
    def action_lyrics_delay_decrease(self):
        """Decrease lyrics timing offset by 0.5s"""
        lyrics_panel = self.query_one("#lyrics-panel", LyricsPanel)
        if lyrics_panel.synced_lyrics:
            lyrics_panel.adjust_timing(-0.5)
            self.notify(f"⏱️ Lyrics offset: {lyrics_panel.timing_offset:+.1f}s")
        else:
            self.notify("⚠️ No synced lyrics loaded")
    
    def on_unmount(self):
        """Cleanup on exit"""
        self.player.cleanup()
        self.playlist_manager.save_all()


if __name__ == "__main__":
    app = YouTubeMusicTUI()
    app.run()
