import spotipy
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
import os
import threading

# =========================================================
# ĐIỀN THÔNG TIN API CỦA BẠN VÀO ĐÂY ĐỂ LẤY NHẠC REAL-TIME:
SPOTIFY_CLIENT_ID = 'd3fd8ea150af48ef9d78e63e075beefb'
SPOTIFY_CLIENT_SECRET = '309e1ac2a7ed4e688f30c27d492925a4'
# =========================================================

auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET) if SPOTIFY_CLIENT_ID else None
sp = spotipy.Spotify(auth_manager=auth_manager) if auth_manager else None

emotion_dict = {0:"Angry",1:"Disgusted",2:"Fearful",3:"Happy",4:"Neutral",5:"Sad",6:"Surprised"}
music_dist = {
    0:"0l9dAmBrUJLylii66JOsHB",
    1:"1n6cpWo9ant4WguEo91KZh",
    2:"4cllEPvFdoX6NIVWPKai9I",
    3:"0deORnapZgrxFY4nsKr9JA",
    4:"4kvSlabrnfRCQWfN0MgtgA",
    5:"1n6cpWo9ant4WguEo91KZh",
    6:"37i9dQZEVXbMDoHDwVN2tF"
}

# Cache lưu trữ tạm thời các playlist đã tải để tránh gọi API liên tục
playlist_cache = {}
fetching_emotions = set()  # Theo dõi các cảm xúc đang được gọi API

def fetch_spotify_background(emotion_idx, emotion_name):
    """ Hàm chạy ngầm để lấy dữ liệu từ Spotify mà không làm treo Camera """
    try:
        results = sp.search(q=emotion_name, limit=15, type='track')
        track_list = []
        for track in results['tracks']['items']:
            name = track['name']
            album = track['album']['name']
            artist = track['album']['artists'][0]['name'] if track['album']['artists'] else "Unknown"
            track_list.append([name, album, artist])
                
        df = pd.DataFrame(track_list, columns=['Name', 'Album', 'Artist'])
        playlist_cache[emotion_idx] = df
    except Exception as e:
        print(f"Lỗi gọi Spotify API: {e}")
    finally:
        if emotion_idx in fetching_emotions:
            fetching_emotions.remove(emotion_idx)

def get_dynamic_playlist(emotion_idx):
    """
    Lấy danh sách nhạc linh hoạt theo thời gian thực từ Spotify.
    Sử dụng luồng (thread) chạy ngầm để không làm lag camera, nhưng nếu không có file CSV dự phòng thì bắt buộc phải chờ API.
    """
    # 1. Trả về Cache nếu đã lấy gần đây
    if emotion_idx in playlist_cache:
        return playlist_cache[emotion_idx]
        
    emotion_name = emotion_dict.get(emotion_idx, "pop").lower()
    csv_path = f"songs/{emotion_name}.csv"
    
    # Nếu chưa điền API Key
    if not sp:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            return df[['Name', 'Album', 'Artist']].head(15)
        return pd.DataFrame(columns=['Name', 'Album', 'Artist'])
        
    # 2. ĐÃ CÓ API KEY: 
    # Nếu có file CSV, ta trả về CSV tạm để chống lag (Zero Lag), đồng thời kích hoạt 1 luồng ngầm đi lấy nhạc Spotify.
    if os.path.exists(csv_path):
        if emotion_idx not in fetching_emotions:
            fetching_emotions.add(emotion_idx)
            threading.Thread(target=fetch_spotify_background, args=(emotion_idx, emotion_name)).start()
        
        df = pd.read_csv(csv_path)
        return df[['Name', 'Album', 'Artist']].head(15)
        
    # 3. TRƯỜNG HỢP KHÔNG CÓ FILE CSV (Bạn vừa xóa file đi để test)
    # Lúc này bắt buộc phải BẤT ĐỘNG (chờ khoảng 0.5 - 1s) để hệ thống chạy API trực tiếp và lấy nhạc về, nếu không web sẽ bị trống trơn.
    fetch_spotify_background(emotion_idx, emotion_name)
    
    if emotion_idx in playlist_cache:
        return playlist_cache[emotion_idx]
        
    return pd.DataFrame(columns=['Name', 'Album', 'Artist'])