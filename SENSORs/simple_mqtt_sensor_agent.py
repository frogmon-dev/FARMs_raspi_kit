import time
import json
from datetime import datetime
import paho.mqtt.client as mqtt

# 설정 파일 경로
setupFileName = '/home/pi/FARMs_raspi_kit/bin/setup.ini'

# MQTT 정보 불러오기
userId   = 'frogmon'
deviceId = 'sensor01'

mqttUrl  = 'frogmon.synology.me'
mqttPort = 8359
pubTopic = 'FARMs/Status/' + userId + '/' + deviceId

# 센서 데이터와 제어 설정을 저장할 전역 변수
sensor_data = None
control_settings = {
    'high': 30.0,      # 고온 임계값 (냉방 작동)
    'low': 20.0,       # 저온 임계값 (난방 작동)
    'status': 'on'      # 제어 상태 (on/off)
}
mqtt_client = None

# MQTT 콜백 함수들 (VERSION2 API 호환)
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"MQTT 브로커에 연결됨: {rc}")
    
    # 센서 데이터를 구독할 토픽
    sensor_topic = f"FARMs/Status/frogmon/temper01"
    client.subscribe(sensor_topic)
    print(f"센서 토픽 구독: {sensor_topic}")
    
    # 제어 설정을 수신할 토픽
    control_topic = f"FARMs/Control/{userId}/{deviceId}"
    client.subscribe(control_topic)
    print(f"제어 토픽 구독: {control_topic}")

def on_message(client, userdata, msg, properties=None):
    global sensor_data, control_settings
    
    try:
        payload = json.loads(msg.payload.decode())
        topic = msg.topic
        print(f"토픽 '{topic}'에서 메시지 수신: {payload}")
        
        # 센서 데이터 토픽인 경우
        if topic == f"FARMs/Status/frogmon/temper01":
            # 센서 에러가 없고 필수 데이터가 있는 경우에만 저장
            if (not payload.get('sensorError', True) and 
                'temperature' in payload and 
                'humidity' in payload):
                sensor_data = {
                    "temperature": payload['temperature'],
                    "humidity": payload['humidity'],
                    "timestamp": payload.get('timestamp', datetime.now().timestamp())
                }
                print("센서 데이터 업데이트 완료")
            else:
                print("센서 에러가 있거나 필수 데이터가 누락되었습니다.")
                sensor_data = None
        
        # 제어 설정 토픽인 경우
        elif topic == f"FARMs/Control/{userId}/{deviceId}":
            update_control_settings(payload)
            
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}")
    except Exception as e:
        print(f"메시지 처리 오류: {e}")

# MQTT 클라이언트 초기화 및 연결
def init_mqtt_client():
    global mqtt_client
    # 최신 API 버전 사용 (DeprecationWarning 해결)
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect(mqttUrl, mqttPort, 60)
        mqtt_client.loop_start()
        print("MQTT 클라이언트 초기화 완료")
        return True
    except Exception as e:
        print(f"MQTT 연결 실패: {e}")
        return False

# 제어 설정 업데이트 함수
def update_control_settings(data):
    """
    수신된 JSON 데이터를 처리하여 제어 설정을 업데이트합니다.
    
    Args:
    - data (dict): 수신된 JSON 데이터
    """
    global control_settings
    try:
        # 제어 설정의 키 목록 (이 키들만 처리)
        control_keys = ['high', 'low', 'status']
        
        # 수신된 데이터의 키가 제어 설정의 키와 일치하는지 확인
        updated_keys = []
        ignored_keys = []
        
        for key, value in data.items():
            if key in control_keys:
                # status 키의 경우 on/off 값만 허용
                if key == 'status':
                    if value.lower() in ['on', 'off']:
                        control_settings[key] = value.lower()
                        updated_keys.append(f"{key}={value.lower()}")
                    else:
                        print(f"status 값은 'on' 또는 'off'만 가능합니다. (받은 값: {value})")
                else:
                    # high, low 키의 경우 숫자로 변환
                    try:
                        control_settings[key] = float(value)
                        updated_keys.append(f"{key}={value}")
                    except ValueError:
                        print(f"{key} 값은 숫자여야 합니다. (받은 값: {value})")
            else:
                # 알 수 없는 키는 무시하고 기록
                ignored_keys.append(key)
        
        # 업데이트 결과 출력
        if updated_keys:
            print(f"제어 설정 업데이트 완료: {', '.join(updated_keys)}")
        
        if ignored_keys:
            print(f"무시된 키 (처리하지 않음): {', '.join(ignored_keys)}")
                
    except Exception as e:
        print(f"제어 설정 업데이트 중 오류 발생: {e}")
        print(f"수신된 데이터: {data}")

# 센서 데이터 읽기 (MQTT에서 수신된 데이터 반환)
def read_sensor_data():
    global sensor_data
    if sensor_data:
        return sensor_data
    else:
        print("센서 데이터를 수신하지 못했습니다.")
        return None

def read_control():
    # 전역 변수에서 제어 설정 반환
    global control_settings
    return control_settings

def make_control_message(motor_id, control_data, current_temp, high_temp, low_temp):
    control_message = {}
    subTopic = 'FARMs/Control/' + userId + '/' + motor_id  # 제어 토픽
    
    if 'high' in control_data and current_temp > high_temp:
        print(f"온도가 높습니다 ({current_temp}°C > {high_temp}°C). 냉방 작동")
        control_message = '{"remote":2,"motor":"up"}'
    elif 'low' in control_data and current_temp < low_temp:
        print(f"온도가 낮습니다 ({current_temp}°C < {low_temp}°C). 난방 작동")
        control_message = '{"remote":2,"motor":"down"}'
    elif 'high' in control_data and 'low' in control_data and low_temp <= current_temp <= high_temp:
        print(f"온도가 적정 범위입니다 ({low_temp}°C <= {current_temp}°C <= {high_temp}°C). 정지")
        control_message = '{"remote":2,"motor":"stop"}'
    return subTopic, control_message

# 데이터 전송 루프
def sensor_loop():
    # MQTT 클라이언트 초기화
    if not init_mqtt_client():
        print("MQTT 클라이언트 초기화 실패. 프로그램을 종료합니다.")
        return
    
    print("센서 데이터 수신 대기 중... (5초 후 시작)")
    time.sleep(5)  # 초기 데이터 수신을 위한 대기
    
    while True:
        sensor_data = read_sensor_data()
        control_data = read_control()
        print("센서 데이터:", sensor_data)
        print("제어 데이터:", control_data)
        
        if sensor_data:  # sensor_data가 None이 아닐 때만 처리
            combined_data = {
                **sensor_data,
                **control_data,
                "timestamp": datetime.now().isoformat()
            }
            print("전송할 데이터:", combined_data)
            
            # MQTT로 데이터 발행
            try:
                mqtt_client.publish(pubTopic, json.dumps(combined_data))
                print("서버로 전송 완료")
            except Exception as e:
                print(f"데이터 전송 실패: {e}")

            # 온도 제어 로직
            current_temp = sensor_data['temperature']
            high_temp = float(control_data.get('high', 0))
            low_temp = float(control_data.get('low', 0))
            status = control_data.get('status', 'off').lower()

            # status가 'on'일 때만 제어 실행
            if status == 'on':
                motor_id = 'motor01,motor02'  # 하드코딩된 모터 ID

                for motor in motor_id.split(','):
                    subTopic, control_message = make_control_message(motor, control_data, current_temp, high_temp, low_temp)
                    print(f"제어 메시지: {control_message} 전송 주소: {subTopic}")
                    
                    # MQTT로 제어 메시지 발행
                    try:
                        mqtt_client.publish(subTopic, control_message)
                        print(f"제어 메시지 전송 완료: {control_message}")
                    except Exception as e:
                        print(f"제어 메시지 전송 실패: {e}")
            else:
                print("제어 상태가 'off'입니다. 제어를 실행하지 않습니다.")
            
        else:
            print("센서 데이터를 수신하지 못했습니다. 10초 후 재시도합니다.")

        time.sleep(10)

if __name__ == '__main__':
    try:
        sensor_loop()
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()