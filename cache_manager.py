"""
Download and cache manager for offline playback
"""
import os
import yt_dlp
from typing import Optional, Dict
import hashlib
import json


class CacheManager:
    """Download and cache audio files for offline play"""
    
    def __init__(self, cache_dir: str = "./.music_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        self.metadata_file = os.path.join(cache_dir, "metadata.json")
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load cache metadata"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_metadata(self):
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Metadata save error: {e}")
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def is_cached(self, url: str) -> bool:
        """Check if URL is cached"""
        cache_key = self._get_cache_key(url)
        if cache_key in self.metadata:
            filepath = self.metadata[cache_key].get('filepath')
            return filepath and os.path.exists(filepath)
        return False
    
    def get_cached_file(self, url: str) -> Optional[str]:
        """Get cached file path"""
        cache_key = self._get_cache_key(url)
        if cache_key in self.metadata:
            filepath = self.metadata[cache_key].get('filepath')
            if filepath and os.path.exists(filepath):
                return filepath
        return None
    
    def download_and_cache(self, url: str, title: str = "") -> Optional[str]:
        """Download and cache audio file"""
        try:
            cache_key = self._get_cache_key(url)
            
            # Check if already cached
            if self.is_cached(url):
                return self.get_cached_file(url)
            
            # Download
            output_template = os.path.join(self.cache_dir, f"{cache_key}.%(ext)s")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Find downloaded file
                audio_file = os.path.join(self.cache_dir, f"{cache_key}.mp3")
                
                if not os.path.exists(audio_file):
                    # Try other extensions
                    for ext in ['opus', 'webm', 'm4a', 'ogg']:
                        alt_file = os.path.join(self.cache_dir, f"{cache_key}.{ext}")
                        if os.path.exists(alt_file):
                            audio_file = alt_file
                            break
                
                if not os.path.exists(audio_file):
                    return None
                
                # Save metadata
                self.metadata[cache_key] = {
                    'url': url,
                    'title': title or info.get('title', 'Unknown'),
                    'filepath': audio_file,
                    'duration': info.get('duration', 0),
                    'cached_at': __import__('datetime').datetime.now().isoformat()
                }
                self._save_metadata()
                
                return audio_file
        
        except Exception as e:
            print(f"Download error: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached files"""
        try:
            for cache_key, data in self.metadata.items():
                filepath = data.get('filepath')
                if filepath and os.path.exists(filepath):
                    os.remove(filepath)
            
            self.metadata = {}
            self._save_metadata()
        except Exception as e:
            print(f"Clear cache error: {e}")
    
    def get_cache_size(self) -> int:
        """Get total cache size in bytes"""
        total_size = 0
        for cache_key, data in self.metadata.items():
            filepath = data.get('filepath')
            if filepath and os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
        return total_size
