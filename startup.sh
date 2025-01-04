#!/home/ytalarm/youtube_alarm_clock/venv/bin/python
/home/ytalarm/youtube_alarm_clock/venv/bin/gunicorn -b 0.0.0.0:8000 --chdir /home/ytalarm/youtube_alarm_clock app:app
