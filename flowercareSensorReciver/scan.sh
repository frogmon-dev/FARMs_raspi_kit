#!/bin/bash

# 현재 사용자 크론탭 내용 삭제
crontab -r
echo "Crontab contents have been deleted."

sleep 5

sudo python sensor_scan.py

# 새로운 크론탭 내용 추가
echo "* * * * * python /home/pi/WATERs/src/sensorData.py" | crontab -
echo "New crontab entry added: '* * * * * python /home/pi/WATERs/src/sensorData.py'"