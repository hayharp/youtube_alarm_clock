'''Grabs videos from YouTube and extracts an audio stream from the desired video'''

import configparser, json, time
from threading import Thread
from yt_dlp import YoutubeDL

import alarm_manager

config = configparser.ConfigParser()
config.read('settings.ini')

CHANNEL = config['YouTube']['Channel']
CACHE_LENGTH = int(config['YouTube']['CacheLength'])

SCRAPE_OPTIONS = {
    'simulate': True,
    'extract_flat': True,
    'quiet': True,
    'no_warnings': True,
    'clean_infojson': True
}

AUDIO_EXTRACT_OPTIONS = {
    'language': 'en',
    'quiet': True,
    'no_warnings': True,
    'format': 'm4a',
    'no_write_comments': True,
    'ignore_dynamic_mpd': True,
    'extract_flat': True,
    'overwrites': True,
    'extractor_args': {
        'youtube': {
            'lang': ['en'],
            'skip': ['hls', 'dash', 'translated_subs'],
            'player_client': ['mweb'],
            'max_comments': [0, 0, 0, 0],
        }
    },
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a'
    }],
    'outtmpl': {
        'default': 'extracted_audio.m4a'
    }
}


def check_cache(target):
    '''Checks for a cache, and uses that instead of scraping if it's recent
    Always rescrapes if the channel URL has been changed'''
    with open('cache.json', 'r') as f:
        cache = json.load(f)
    if cache['channel'] != CHANNEL:
        return False
    try:
        if int(time.time()) - int(cache[target]['timestamp']) < CACHE_LENGTH:
            return cache[target]
    except KeyError:
        return False
    return False

def refresh_cache(target, content):
    '''Refreshes a component of the cache'''
    with open('cache.json', 'r') as f:
        cache = json.load(f)
    cache[target] = content
    try:
        cache[target]['timestamp'] = time.time()
    except TypeError:
        pass
    cache['channel'] = CHANNEL
    with open('cache.json', 'w') as f:
        json.dump(cache, f, indent=4)

def get_playlists():
    '''Scrapes channel for playlist names and urls'''
    cache = check_cache('playlists')
    if cache:
        return cache
    with YoutubeDL(SCRAPE_OPTIONS) as ytdl:
        channel_metadata = ytdl.sanitize_info(ytdl.extract_info(CHANNEL))
    playlists = {}
    for playlist in channel_metadata['entries']:
        playlists[playlist['title']] = playlist['url']
    refresh_cache('playlists', playlists)
    return playlists

def get_videos(playlist_url):
    cache = check_cache(playlist_url)
    if cache:
        return cache
    with YoutubeDL(SCRAPE_OPTIONS) as ytdl:
        playlist_metadata = ytdl.sanitize_info(ytdl.extract_info(playlist_url))
    videos = {}
    for video in playlist_metadata['entries']:
        videos[video['title']] = video['url']
    refresh_cache(playlist_url, videos)
    return videos

def extract_audio(video_url):
    with YoutubeDL(AUDIO_EXTRACT_OPTIONS) as ytdl:
        # alarm_manager.set_video_name(ytdl.sanitize_info(ytdl.extract_info(video_url))['title'])
        ytdl.download(video_url)
    
def extract_audio_bg(video_url):
    thread = Thread(target=extract_audio, args=[video_url])
    thread.start()
