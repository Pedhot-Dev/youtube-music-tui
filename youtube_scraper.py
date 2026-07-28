import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict, Optional


class YouTubeScraper:
    """Scrape YouTube search results tanpa API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search YouTube videos"""
        url = f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Extract ytInitialData from page
            pattern = r'var ytInitialData = ({.*?});'
            match = re.search(pattern, response.text)
            
            if not match:
                return []
            
            data = json.loads(match.group(1))
            
            # Navigate the JSON structure
            contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
            
            results = []
            for content in contents:
                if 'itemSectionRenderer' in content:
                    items = content['itemSectionRenderer'].get('contents', [])
                    
                    for item in items:
                        if 'videoRenderer' in item:
                            video = item['videoRenderer']
                            
                            video_id = video.get('videoId')
                            if not video_id:
                                continue
                            
                            title = video.get('title', {}).get('runs', [{}])[0].get('text', 'Unknown')
                            
                            # Duration
                            duration_text = ''
                            if 'lengthText' in video:
                                duration_text = video['lengthText'].get('simpleText', '')
                            
                            # Channel
                            channel = ''
                            if 'ownerText' in video:
                                channel = video['ownerText'].get('runs', [{}])[0].get('text', '')
                            
                            # Views
                            views = ''
                            if 'viewCountText' in video:
                                views = video['viewCountText'].get('simpleText', '')
                            
                            results.append({
                                'id': video_id,
                                'title': title,
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                                'duration': duration_text,
                                'channel': channel,
                                'views': views
                            })
                            
                            if len(results) >= max_results:
                                break
                
                if len(results) >= max_results:
                    break
            
            return results
        
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """Get video info from direct URL"""
        try:
            video_id_pattern = r'(?:v=|\/)([a-zA-Z0-9_-]{11})'
            match = re.search(video_id_pattern, url)
            
            if not match:
                return None
            
            video_id = match.group(1)
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            response = self.session.get(video_url)
            response.raise_for_status()
            
            # Extract title
            title_pattern = r'<title>(.*?)</title>'
            title_match = re.search(title_pattern, response.text)
            title = title_match.group(1).replace(' - YouTube', '') if title_match else 'Unknown'
            
            return {
                'id': video_id,
                'title': title,
                'url': video_url
            }
        
        except Exception as e:
            print(f"Get video info error: {e}")
            return None
    
    def is_playlist_url(self, url: str) -> bool:
        """Check if URL is a playlist"""
        return 'list=' in url or '/playlist?' in url
    
    def get_playlist_videos(self, url: str, max_videos: int = 100) -> List[Dict]:
        """Fetch all videos from a YouTube playlist"""
        try:
            # Extract playlist ID
            playlist_id_pattern = r'[?&]list=([a-zA-Z0-9_-]+)'
            match = re.search(playlist_id_pattern, url)
            
            if not match:
                return []
            
            playlist_id = match.group(1)
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            
            response = self.session.get(playlist_url)
            response.raise_for_status()
            
            # Extract ytInitialData
            pattern = r'var ytInitialData = ({.*?});'
            data_match = re.search(pattern, response.text)
            
            if not data_match:
                return []
            
            data = json.loads(data_match.group(1))
            
            # Navigate to playlist items
            try:
                contents = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']
            except (KeyError, IndexError):
                return []
            
            results = []
            for item in contents:
                if 'playlistVideoRenderer' not in item:
                    continue
                
                video = item['playlistVideoRenderer']
                
                video_id = video.get('videoId')
                if not video_id:
                    continue
                
                # Title
                title = 'Unknown'
                if 'title' in video:
                    runs = video['title'].get('runs', [])
                    if runs:
                        title = runs[0].get('text', 'Unknown')
                
                # Duration
                duration_text = ''
                if 'lengthText' in video:
                    duration_text = video['lengthText'].get('simpleText', '')
                
                # Channel
                channel = ''
                if 'shortBylineText' in video:
                    runs = video['shortBylineText'].get('runs', [])
                    if runs:
                        channel = runs[0].get('text', '')
                
                results.append({
                    'id': video_id,
                    'title': title,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'duration': duration_text,
                    'channel': channel,
                })
                
                if len(results) >= max_videos:
                    break
            
            return results
        
        except Exception as e:
            print(f"Playlist fetch error: {e}")
            return []
