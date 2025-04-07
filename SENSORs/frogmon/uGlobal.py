#uGlobal.py

import os
import re
import json
import subprocess
import socket
import csv
import configparser
import paho.mqtt.client as mqtt
import time


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
    
    def set_ini_value(filename, section, key, value):
        """
        INI 파일의 특정 section과 key에 값을 설정하는 함수.
        section이 없으면 새로 생성하고, key가 없으면 새로 추가합니다.

        Args:
        - filename (str): INI 파일의 이름.
        - section (str): 설정할 섹션 이름.
        - key (str): 설정할 키 이름.
        - value (str): 설정할 값.

        Returns:
        - bool: 성공하면 True, 실패하면 False.
        """
        try:
            config = configparser.ConfigParser()
            
            # 파일이 존재하면 읽기
            if os.path.exists(filename):
                config.read(filename)
            
            # section이 없으면 생성
            if not config.has_section(section):
                config.add_section(section)
            
            # key와 value 설정
            config.set(section, key, str(value))
            
            # 파일 저장
            with open(filename, 'w') as f:
                config.write(f)
            
            return True
            
        except Exception as e:
            print(f"INI 파일 설정 중 오류 발생: {e}")
            return False
    
    def get_ini_section(filename, section):
        """
        INI 파일에서 특정 section을 반환하는 함수.

        Args:
        - filename (str): INI 파일의 이름.  
        - section (str): 찾을 섹션 이름.

        Returns:
        - dict: 해당 section의 모든 키와 값이 포함된 딕셔너리.
        """
        config = configparser.ConfigParser()    
        config.read(filename)
        
        if config.has_section(section):
            return config.items(section)
        else:
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

    def mqtt_subscribe(mqttUrl, mqttPort, subTopic, on_message, client_id=None, max_retries=5, retry_delay=5):
        """
        MQTT 서버에 연결하고 지정된 토픽을 구독하는 함수.
        메시지 수신 시 on_message 콜백 함수를 호출합니다.
        연결 실패 시 재시도합니다.

        Args:
        - mqttUrl (str): MQTT 서버의 URL 또는 IP 주소.
        - mqttPort (int): MQTT 서버의 포트 번호.
        - subTopic (str): 구독할 토픽 이름.
        - on_message (function): 메시지 수신 시 호출할 콜백 함수.
        - client_id (str, optional): MQTT 클라이언트 ID. 기본값은 None.
        - max_retries (int, optional): 최대 재시도 횟수. 기본값은 5.
        - retry_delay (int, optional): 재시도 간격(초). 기본값은 5.

        Returns:
        - mqtt.Client: MQTT 클라이언트 객체.
        """
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                # MQTT 클라이언트 생성
                client = mqtt.Client(client_id=client_id)
                
                # 콜백 함수 설정
                client.on_message = on_message
                
                # MQTT 서버에 연결
                client.connect(mqttUrl, mqttPort, 60)
                print(f"MQTT 서버 연결 성공: {mqttUrl}:{mqttPort}")
                
                # 토픽 구독
                client.subscribe(subTopic)
                print(f"토픽 구독 성공: {subTopic}")
                
                # 메시지 수신 루프 시작
                client.loop_start()
                print("메시지 수신 대기 중...")
                
                return client
                
            except Exception as e:
                last_error = e
                retry_count += 1
                print(f"MQTT 연결 시도 {retry_count}/{max_retries} 실패: {e}")
                
                if retry_count < max_retries:
                    print(f"{retry_delay}초 후 재시도합니다...")
                    time.sleep(retry_delay)
                else:
                    print(f"최대 재시도 횟수({max_retries}회)를 초과했습니다.")
                    print(f"마지막 오류: {last_error}")
                    return None