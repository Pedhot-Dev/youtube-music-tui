from typing import Optional, Tuple, Dict, List
import requests
import re


class LRCLibFetcher:
    """Fetch synced lyrics from lrclib.net"""
    
    def __init__(self):
        self.base_url = "https://lrclib.net/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'YouTube-Music-TUI/1.0'
        })
    
    def fetch(self, track_name: str, artist_name: str, album_name: str = "", duration: int = 0) -> Optional[Dict]:
        """
        Fetch lyrics from lrclib.net
        Returns dict with 'plainLyrics', 'syncedLyrics', 'duration', etc.
        """
        try:
            params = {
                'track_name': track_name,
                'artist_name': artist_name,
            }
            
            if album_name:
                params['album_name'] = album_name
            
            if duration > 0:
                params['duration'] = duration
            
            response = self.session.get(
                f"{self.base_url}/get",
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                return None
        
        except Exception as e:
            print(f"LRCLib fetch error: {e}")
            return None
    
    def parse_lrc(self, synced_lyrics: str) -> List[Tuple[float, str]]:
        """
        Parse LRC format to list of (timestamp, line) tuples
        Example: "[00:17.12] I feel your breath on my neck" -> (17.12, "I feel your breath on my neck")
        """
        lines = []
        
        if not synced_lyrics:
            return lines
        
        # LRC format: [MM:SS.xx] text
        pattern = r'\[(\d+):(\d+)\.(\d+)\](.*)'
        
        for line in synced_lyrics.split('\n'):
            match = re.match(pattern, line)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                centiseconds = int(match.group(3))
                text = match.group(4).strip()
                
                # Convert to total seconds
                timestamp = minutes * 60 + seconds + centiseconds / 100.0
                
                lines.append((timestamp, text))
        
        return lines


class LyricsFetcher:
    """Fetch lyrics with lrclib.net priority and synced lyrics support"""
    
    def __init__(self):
        self.lrclib = LRCLibFetcher()
        # Fallback to multi-provider if lrclib fails
        try:
            from lyricsfetch.fetcher import fetch_lyrics as fetch_lyrics_multi_provider
            from lyricsfetch.metadata import parse_title, clean_song_title
            self.fallback_fetcher = fetch_lyrics_multi_provider
            self.parse_title = parse_title
            self.clean_song_title = clean_song_title
        except:
            self.fallback_fetcher = None
            self.parse_title = None
            self.clean_song_title = None
    
    def fetch_lyrics(self, title: str, artist: str = "", album: str = "", duration: int = 0) -> Dict:
        """
        Fetch lyrics by title and artist
        Returns dict with:
        - 'text': lyrics text
        - 'synced': list of (timestamp, line) if available
        - 'provider': source name
        """
        try:
            # Try lrclib.net first
            lrc_data = self.lrclib.fetch(title, artist, album, duration)
            
            if lrc_data:
                synced = None
                if lrc_data.get('syncedLyrics'):
                    synced = self.lrclib.parse_lrc(lrc_data['syncedLyrics'])
                
                plain = lrc_data.get('plainLyrics', '')
                
                return {
                    'text': plain,
                    'synced': synced,
                    'provider': 'lrclib.net',
                    'metadata': {
                        'artist': lrc_data.get('artistName', ''),
                        'track': lrc_data.get('trackName', ''),
                        'album': lrc_data.get('albumName', ''),
                        'duration': lrc_data.get('duration', 0)
                    }
                }
            
            # Fallback to multi-provider
            if self.fallback_fetcher:
                clean_title = self.clean_song_title(title) if self.clean_song_title else title
                lyrics, provider = self.fallback_fetcher(artist, clean_title)
                
                if lyrics:
                    return {
                        'text': lyrics,
                        'synced': None,
                        'provider': provider
                    }
            
            return {
                'text': 'Lyrics not found from any provider',
                'synced': None,
                'provider': 'none'
            }
        
        except Exception as e:
            return {
                'text': f'Error fetching lyrics: {e}',
                'synced': None,
                'provider': 'error'
            }
    
    def fetch_lyrics_from_video_title(self, video_title: str, duration: int = 0) -> Dict:
        """Extract artist/title from video title and fetch lyrics"""
        try:
            artist = ""
            track = ""
            album = ""
            
            # Try parsing with lyricsfetch parser
            if self.parse_title:
                parsed = self.parse_title(video_title)
                artist = parsed.get('artist', '')
                track = parsed.get('track', '')
            
            # Fallback: split by ' - '
            if not artist or not track:
                if ' - ' in video_title:
                    parts = video_title.split(' - ', 1)
                    if len(parts) == 2:
                        artist = parts[0].strip()
                        track = parts[1].strip()
                        
                        # Remove common suffixes
                        for suffix in ['(Official Video)', '(Official Audio)', '(Lyric Video)', 
                                      '(Official Music Video)', '[Official Video]', '[Official Audio]',
                                      '- Topic']:
                            track = track.replace(suffix, '').strip()
                else:
                    track = video_title
            
            # Try lrclib first
            result = self.fetch_lyrics(track, artist, album, duration)
            
            return result
        
        except Exception as e:
            return {
                'text': f'Error fetching lyrics: {e}',
                'synced': None,
                'provider': 'error'
            }
