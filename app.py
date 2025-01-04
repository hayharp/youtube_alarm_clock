'''The main web interface for the BPAC'''

from flask import Flask, render_template, request

import json
import alarm_manager, yt_audio

app = Flask(__name__)

@app.route('/stop')
def kill_alarm():
    '''Kills the alarm, if necessary'''
    if request.method == 'POST':
        alarm_manager.run_alarm(mode='stop')
        return(200)
    return(405)

@app.route('/alarm', methods=['GET', 'POST'])
def alarm():
    '''Manage the alarm'''

    playlists = yt_audio.get_playlists()

    selector = 'Playlist'
    selector_options = playlists
    message = f'Current alarm set to play {alarm_manager.get_video_name()} at {alarm_manager.get_alarm_time()}'

    if request.method == 'POST':
        if request.form['action'] == 'Playlist Select':
            selector='Video'
            # if request.form['selector'] == 'random':
                # selector_options = yt_audio.get_videos(playlists[random.choice(list(playlists.keys()))])
            # else:
            selector_options = yt_audio.get_videos(playlists[request.form['selector']])
        if request.form['action'] == 'Video Select': # Change to just remember current playlist selection?
            with open('cache.json', 'r') as f:
                cache = json.load(f)
            for item in cache:
                try:
                    url = cache[item][request.form['selector']]
                except (KeyError, TypeError):
                    pass
            alarm_manager.set_video_name(request.form['selector'])
            yt_audio.extract_audio_bg(url)
            message = f"Current alarm set to play {request.form['selector']} at {alarm_manager.get_alarm_time()}"
        if request.form['action'] == 'Set Time':
            if request.form['alarm-time'] == '':
                alarm_manager.remove_alarm()
            else:
                [hour, minute] = request.form['alarm-time'].split(':')
                alarm_manager.set_alarm_time(hour, minute)
            message = f'Current alarm set to play {alarm_manager.get_video_name()} at {alarm_manager.get_alarm_time()}'
        if request.form['action'] == 'Stop Alarm':
            alarm_manager.run_alarm(mode='stop')
            message = f'Alarm stopped! Next alarm set to play {alarm_manager.get_video_name()} at {alarm_manager.get_alarm_time()}'

    return render_template('alarm.html', message=message, selector=selector, selector_options=selector_options)
