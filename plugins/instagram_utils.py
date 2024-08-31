import requests
from bs4 import BeautifulSoup
import re
import io

def get_instagram_media(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    script = soup.find('script', text=re.compile('window\._sharedData'))
    if script:
        shared_data = re.search(r'window\._sharedData = (.+);</script>', script.string)
        if shared_data:
            data = shared_data.group(1)
            data_json = json.loads(data)
            media = data_json['entry_data']['PostPage'][0]['graphql']['shortcode_media']
            media_url = media.get('display_url')
            if media_url:
                return media_url
    return None

def fetch_instagram_media(url):
    media_url = get_instagram_media(url)
    if media_url:
        response = requests.get(media_url)
        if response.status_code == 200:
            return io.BytesIO(response.content)
    return None
