import yt_dlp
import mpv
import threading
import time
from typing import Optional, Callable
import os
import tempfile


class AudioPlayer:
    """Audio player using yt-dlp + python-mpv with real-time volume control"""
    
    def __init__(self):
        self.current_url: Optional[str] = None
        self.is_playing = False
        self.is_paused = False
        self.duration = 0
        self.position = 0
        self.volume = 0.7
        self._stop_flag = False
        self._position_thread = None
        self.on_position_update: Optional[Callable[[float], None]] = None
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize mpv player
        self.player = mpv.MPV(
            video=False,
            ytdl=True,
            input_default_bindings=False,
            input_vo_keyboard=False,
            osc=False
        )
        
        # Set initial volume
        self.player.volume = int(self.volume * 100)
        
        # Register event handlers
        @self.player.event_callback('end-file')
        def on_end_file(event):
            if self.is_playing:
                self.is_playing = False
    
    def download_and_play(self, url: str) -> bool:
        """Stream and play audio"""
        try:
            self.stop()
            self.current_url = url
            
            # Get audio URL using yt-dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
                self.duration = info.get('duration', 0)
            
            # Play with mpv
            self.player.play(audio_url)
            self.player.volume = int(self.volume * 100)
            
            self.is_playing = True
            self.is_paused = False
            self._stop_flag = False
            self.position = 0
            
            # Start position tracking thread
            self._position_thread = threading.Thread(target=self._track_position, daemon=True)
            self._position_thread.start()
            
            return True
        
        except Exception as e:
            print(f"Play error: {e}")
            return False
    
    def _track_position(self):
        """Track playback position"""
        while not self._stop_flag and self.is_playing:
            try:
                if not self.is_paused:
                    # Get position from mpv
                    pos = self.player.time_pos
                    if pos is not None:
                        self.position = pos
                        
                        if self.on_position_update:
                            self.on_position_update(self.position)
                
                time.sleep(0.1)
            except:
                pass
    
    def pause(self):
        """Pause playback"""
        if self.is_playing and not self.is_paused:
            try:
                self.player.pause = True
                self.is_paused = True
            except:
                pass
    
    def resume(self):
        """Resume playback"""
        if self.is_playing and self.is_paused:
            try:
                self.player.pause = False
                self.is_paused = False
            except:
                pass
    
    def toggle_pause(self):
        """Toggle pause/resume"""
        if self.is_paused:
            self.resume()
        else:
            self.pause()
    
    def stop(self):
        """Stop playback"""
        self._stop_flag = True
        
        if self._position_thread:
            self._position_thread.join(timeout=1.0)
        
        try:
            self.player.stop()
        except:
            pass
        
        self.is_playing = False
        self.is_paused = False
        self.position = 0
    
    def set_volume(self, volume: float):
        """Set volume (0.0 - 1.0) with real-time control"""
        self.volume = max(0.0, min(1.0, volume))
        try:
            self.player.volume = int(self.volume * 100)
        except:
            pass
    
    def mute(self):
        """Mute audio"""
        try:
            self.player.mute = True
        except:
            pass
    
    def unmute(self):
        """Unmute audio"""
        try:
            self.player.mute = False
        except:
            pass
    
    def is_muted(self) -> bool:
        """Check if muted"""
        try:
            return self.player.mute
        except:
            return False
    
    def seek(self, position: float):
        """Seek to position (seconds)"""
        try:
            self.player.seek(position, reference='absolute')
            self.position = position
        except:
            pass
    
    def get_status(self) -> dict:
        """Get current player status"""
        return {
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'position': self.position,
            'duration': self.duration,
            'volume': self.volume,
            'url': self.current_url
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop()
        try:
            self.player.terminate()
        except:
            pass
        try:
            os.rmdir(self.temp_dir)
        except:
            pass
