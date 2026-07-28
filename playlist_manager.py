"""
Playlist manager dengan persistence
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class PlaylistManager:
    """Manage playlists, history, and favorites"""
    
    def __init__(self, data_dir: str = "./.music_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.playlist_file = os.path.join(data_dir, "playlist.json")
        self.history_file = os.path.join(data_dir, "history.json")
        self.favorites_file = os.path.join(data_dir, "favorites.json")
        
        self.current_playlist: List[Dict] = []
        self.history: List[Dict] = []
        self.favorites: List[Dict] = []
        self.current_index = -1
        self.shuffle_mode = False
        self.repeat_mode = "none"  # none, one, all
        
        self.load_all()
    
    def load_all(self):
        """Load all data from disk"""
        self.current_playlist = self._load_json(self.playlist_file, [])
        self.history = self._load_json(self.history_file, [])
        self.favorites = self._load_json(self.favorites_file, [])
    
    def save_all(self):
        """Save all data to disk"""
        self._save_json(self.playlist_file, self.current_playlist)
        self._save_json(self.history_file, self.history[-100:])  # Keep last 100
        self._save_json(self.favorites_file, self.favorites)
    
    def _load_json(self, filepath: str, default):
        """Load JSON file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except:
            pass
        return default
    
    def _save_json(self, filepath: str, data):
        """Save JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Save error: {e}")
    
    def add_to_playlist(self, track: Dict):
        """Add track to current playlist"""
        if track not in self.current_playlist:
            self.current_playlist.append(track)
            self.save_all()
    
    def remove_from_playlist(self, index: int):
        """Remove track from playlist"""
        if 0 <= index < len(self.current_playlist):
            self.current_playlist.pop(index)
            if self.current_index >= len(self.current_playlist):
                self.current_index = len(self.current_playlist) - 1
            self.save_all()
    
    def clear_playlist(self):
        """Clear entire playlist"""
        self.current_playlist = []
        self.current_index = -1
        self.save_all()
    
    def add_to_history(self, track: Dict):
        """Add track to history"""
        track_with_time = track.copy()
        track_with_time['played_at'] = datetime.now().isoformat()
        self.history.append(track_with_time)
        self.save_all()
    
    def add_to_favorites(self, track: Dict):
        """Add track to favorites"""
        if track not in self.favorites:
            self.favorites.append(track)
            self.save_all()
            return True
        return False
    
    def remove_from_favorites(self, track: Dict):
        """Remove track from favorites"""
        if track in self.favorites:
            self.favorites.remove(track)
            self.save_all()
            return True
        return False
    
    def is_favorite(self, track: Dict) -> bool:
        """Check if track is in favorites"""
        return any(
            f.get('id') == track.get('id') or f.get('url') == track.get('url')
            for f in self.favorites
        )
    
    def toggle_shuffle(self) -> bool:
        """Toggle shuffle mode"""
        self.shuffle_mode = not self.shuffle_mode
        return self.shuffle_mode
    
    def cycle_repeat(self) -> str:
        """Cycle through repeat modes"""
        modes = ["none", "one", "all"]
        current_idx = modes.index(self.repeat_mode)
        self.repeat_mode = modes[(current_idx + 1) % len(modes)]
        return self.repeat_mode
    
    def get_next_track(self) -> Optional[Dict]:
        """Get next track based on current mode"""
        if not self.current_playlist:
            return None
        
        if self.repeat_mode == "one" and self.current_index >= 0:
            return self.current_playlist[self.current_index]
        
        if self.shuffle_mode:
            import random
            self.current_index = random.randint(0, len(self.current_playlist) - 1)
        else:
            self.current_index += 1
            if self.current_index >= len(self.current_playlist):
                if self.repeat_mode == "all":
                    self.current_index = 0
                else:
                    return None
        
        if 0 <= self.current_index < len(self.current_playlist):
            return self.current_playlist[self.current_index]
        return None
    
    def get_previous_track(self) -> Optional[Dict]:
        """Get previous track"""
        if not self.current_playlist:
            return None
        
        self.current_index -= 1
        if self.current_index < 0:
            if self.repeat_mode == "all":
                self.current_index = len(self.current_playlist) - 1
            else:
                self.current_index = 0
                return None
        
        if 0 <= self.current_index < len(self.current_playlist):
            return self.current_playlist[self.current_index]
        return None
    
    def play_track_at_index(self, index: int) -> Optional[Dict]:
        """Play specific track from playlist"""
        if 0 <= index < len(self.current_playlist):
            self.current_index = index
            return self.current_playlist[index]
        return None
