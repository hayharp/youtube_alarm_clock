'''Handles the actual setting and editing of the alarm with cron'''

import configparser, subprocess

from crontab import CronTab

def set_video_name(video_name):
    '''Sets the current audio variable to match the extracted audio'''
    config = configparser.ConfigParser()
    config.read('settings.ini')
    config['DoNotChange']['currentaudio'] = video_name
    with open('settings.ini', 'w') as f:
        config.write(f)

def get_video_name():
    '''Returns current audio variable'''
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return config['DoNotChange']['currentaudio']

def set_alarm_time(hour, minute):
    '''Sets cron to play the alarm at the chosen time'''
    config = configparser.ConfigParser()
    config.read('settings.ini')
    user = config['Cron']['username']
    alarm_scheduler = CronTab(user=user)
    old_job = alarm_scheduler.find_command('sh')
    alarm_scheduler.remove(old_job)
    alarm = alarm_scheduler.new(command=f'sh /home/{user}/python/bible_project_alarm_clock/play_alarm.sh')
    alarm.hour.on(hour)
    alarm.minute.on(minute)
    alarm_scheduler.write()
    config['DoNotChange']['alarmtime'] = f'{hour},{minute}'
    with open('settings.ini', 'w') as f:
        config.write(f)

def remove_alarm():
    '''Removes the alarm entry from cron entirely'''
    config = configparser.ConfigParser()
    config.read('settings.ini')
    user = config['Cron']['username']
    alarm_scheduler = CronTab(user=user)
    old_job = alarm_scheduler.find_command('sh')
    alarm_scheduler.remove(old_job)
    config['DoNotChange']['alarmtime'] = ''
    with open('settings.ini', 'w') as f:
        config.write(f)

def get_alarm_time(military=False):
    '''Returns the current set time for the alarm'''
    config = configparser.ConfigParser()
    config.read('settings.ini')
    if config['DoNotChange']['alarmtime'] == '':
        return '[NOT SET]'
    [hour, minute] = config['DoNotChange']['alarmtime'].split(',')
    if military:
        return f'{hour}:{minute}'
    if int(hour) > 12:
        return f'{int(hour) - 12}:{minute} PM'
    return f'{hour}:{minute} AM'

def run_alarm(mode='play'):
    '''Runs or stops the alarm'''
    if mode == 'play':
        subprocess.Popen(['ffplay', 'extracted_audio.m4a', '-loglevel', '-8'])
    if mode == 'stop':
        subprocess.Popen(['killall', 'ffplay'])