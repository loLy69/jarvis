import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

def get_current_track():
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope="user-read-playback-state user-read-currently-playing",
            cache_path=".spotify_cache"
        ))
        
        current = sp.current_playback()
        if current and current.get('item'):
            track = current['item']
            return {
                'artist': track['artists'][0]['name'],
                'track': track['name'],
                'album': track['album']['name']
            }
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    print("Проверяем текущий трек...")
    result = get_current_track()
    if result:
        print(f"Играет: {result['artist']} - {result['track']}")
    else:
        print("Ничего не играет или ошибка")
