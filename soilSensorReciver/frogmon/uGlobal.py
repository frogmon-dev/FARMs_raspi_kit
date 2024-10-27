#uGlobal.py

import os
import re
import json
import subprocess
import socket
import csv
import configparser
import paho.mqtt.client as mqtt


#from unidecode       import unidecode
from datetime import datetime, timedelta

class GLOB:
    def __init__(self):
        print('init')

    def get_ini_value(filename, section, key, defult):
        """
        INI 파일에서 특정 section과 key에 해당하는 값을 반환하는 함수.

        Args:
        - filename (str): INI 파일의 이름.
        - section (str): 찾을 섹션 이름.
        - key (str): 찾을 키 이름.

        Returns:
        - str: 해당 section과 key에 대한 값. 섹션 또는 키가 없으면 None 반환.
        """
        config = configparser.ConfigParser()
        config.read(filename)
        
        # section과 key가 존재하는지 확인 후 값 반환
        if config.has_section(section):
            if config.has_option(section, key):
                return config.get(section, key)
            else:
                print(f"'{key}' 키가 '{section}' 섹션에 존재하지 않습니다.")
                return defult
        else:
            print(f"'{section}' 섹션이 INI 파일에 존재하지 않습니다.")
            return defult
        
        return None
    
    def save_sensor_data_to_csv(filename, sensor_data):
        """
        sensor_data를 입력된 filename으로 CSV 파일로 저장하고, 현재 시간을 첫 번째 열에 추가하는 함수.
        
        Args:
        - filename (str): 저장할 파일의 이름 (확장자 .csv 포함).
        - sensor_data (dict): 센서 데이터가 포함된 딕셔너리. 예: {"humidity": 45.6, "temperature": 22.3, ...}
        """
        # 파일 존재 여부 확인
        file_exists = os.path.isfile(filename)
        
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            
            # 파일이 없으면 헤더 추가
            if not file_exists:
                header = ["datetime"] + list(sensor_data.keys())  # 시간 컬럼을 추가한 헤더
                writer.writerow(header)
            
            # 현재 시간을 HH:MM:SS 형식으로 추가
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # 데이터 작성
            row = [current_time] + list(sensor_data.values())
            writer.writerow(row)

    def mqtt_publish(mqttUrl, mqttPort, pubTopic, value):
        """
        MQTT 서버에 연결하고 지정된 토픽에 값을 게시하는 함수.
        value가 dict일 경우 JSON 형식으로 변환하여 게시합니다.

        Args:
        - mqttUrl (str): MQTT 서버의 URL 또는 IP 주소.
        - mqttPort (int): MQTT 서버의 포트 번호.
        - pubTopic (str): 게시할 토픽 이름.
        - value (dict): 게시할 값. dict일 경우 JSON으로 변환됩니다.
        """        
        # MQTT 클라이언트 생성
        client = mqtt.Client()
        
        # MQTT 서버에 연결
        client.connect(mqttUrl, mqttPort, 60)
        
        # dict 값을 JSON 형식으로 변환
        if isinstance(value, dict):
            value = json.dumps(value)
        
        # 지정된 토픽에 값 게시
        client.publish(pubTopic, value)
        
        # 연결 종료
        client.disconnect()