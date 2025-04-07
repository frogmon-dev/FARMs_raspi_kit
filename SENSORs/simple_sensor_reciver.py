import time
import json
from datetime import datetime
from frogmon.uGlobal import GLOB

# 설정 파일 경로
setupFileName = '/home/pi/FARMs_raspi_kit/bin/setup.ini'

# MQTT 정보 불러오기
userId   = GLOB.get_ini_value(setupFileName, 'SETUP', 'user_id', 'test')
deviceId = GLOB.get_ini_value(setupFileName, 'AGENT', 'id', 'test')

mqttUrl  = GLOB.get_ini_value(setupFileName, 'MQTT', 'url', 'frogmon.synology.me')
mqttPort = int(GLOB.get_ini_value(setupFileName, 'MQTT', 'port', '8359'))
subTopic = GLOB.get_ini_value(setupFileName, 'MQTT', 'sub_topic', 'test') + userId + '/' + deviceId

def update_control_settings(data):
    """
    수신된 JSON 데이터를 처리하여 CONTROL 섹션의 설정을 업데이트합니다.
    
    Args:
    - data (dict): 수신된 JSON 데이터
    """
    try:
        # CONTROL 섹션의 키 목록
        control_keys = ['high', 'low', 'status']
        
        # 수신된 데이터의 키가 CONTROL 섹션의 키와 일치하는지 확인
        for key, value in data.items():
            if key in control_keys:
                # status 키의 경우 on/off 값만 허용
                if key == 'status':
                    if value.lower() in ['on', 'off']:
                        if GLOB.set_ini_value(setupFileName, 'CONTROL', key, value.lower()):
                            print(f"CONTROL 섹션의 {key} 값을 {value.lower()}로 업데이트했습니다.")
                        else:
                            print(f"CONTROL 섹션의 {key} 값 업데이트에 실패했습니다.")
                    else:
                        print(f"status 값은 'on' 또는 'off'만 가능합니다. (받은 값: {value})")
                else:
                    # high, low 키의 경우 기존 로직대로 처리
                    if GLOB.set_ini_value(setupFileName, 'CONTROL', key, str(value)):
                        print(f"CONTROL 섹션의 {key} 값을 {value}로 업데이트했습니다.")
                    else:
                        print(f"CONTROL 섹션의 {key} 값 업데이트에 실패했습니다.")
            else:
                print(f"알 수 없는 키입니다: {key}")
                
    except Exception as e:
        print(f"설정 업데이트 중 오류 발생: {e}")

def on_message(client, userdata, message):
    try:
        # 메시지 디코딩
        payload = message.payload.decode('utf-8')
        print(f"수신된 메시지: {payload}")
        
        # JSON 파싱
        data = json.loads(payload)
        print(f"파싱된 데이터: {data}")
        
        # CONTROL 섹션 업데이트
        update_control_settings(data)
        
    except Exception as e:
        print(f"메시지 처리 중 오류 발생: {e}")

def main():
    print("MQTT 수신기 시작")
    print(f"연결 정보:")
    print(f"URL: {mqttUrl}")
    print(f"Port: {mqttPort}")
    print(f"Topic: {subTopic}")
    
    # 고유한 클라이언트 ID 생성 (deviceId + '_receiver' + 타임스탬프)
    client_id = f"{deviceId}"
    print(f"Client ID: {client_id}")
    
    # MQTT 클라이언트 설정 및 연결 (최대 5회 재시도, 5초 간격)
    client = GLOB.mqtt_subscribe(mqttUrl, mqttPort, subTopic, on_message, client_id, max_retries=5, retry_delay=5)
    
    if client:
        try:
            while True:
                # 연결 상태 확인
                if not client.is_connected():
                    print("MQTT 연결이 끊어졌습니다. 재연결을 시도합니다...")
                    client.loop_stop()
                    client.disconnect()
                    client = GLOB.mqtt_subscribe(mqttUrl, mqttPort, subTopic, on_message, client_id, max_retries=5, retry_delay=5)
                    if not client:
                        print("재연결 실패. 프로그램을 종료합니다.")
                        break
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n프로그램 종료")
            client.loop_stop()
            client.disconnect()
        except Exception as e:
            print(f"예상치 못한 오류 발생: {e}")
            client.loop_stop()
            client.disconnect()
    else:
        print("MQTT 연결 실패. 프로그램을 종료합니다.")

if __name__ == '__main__':
    main() 