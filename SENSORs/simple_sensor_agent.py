import time
import json
from datetime import datetime
import Adafruit_DHT

from frogmon.uGlobal import GLOB

# DHT11 센서 설정
dht11_sensor = Adafruit_DHT.DHT11
dht11_pin = 2  # 연결된 GPIO 핀 번호

# 설정 파일 경로
setupFileName = '/home/pi/FARMs_raspi_kit/bin/setup.ini'

# MQTT 정보 불러오기
userId   = GLOB.get_ini_value(setupFileName, 'SETUP', 'user_id', 'test')
deviceId = GLOB.get_ini_value(setupFileName, 'AGENT', 'id', 'test')

mqttUrl  = GLOB.get_ini_value(setupFileName, 'MQTT', 'url', 'frogmon.synology.me')
mqttPort = int(GLOB.get_ini_value(setupFileName, 'MQTT', 'port', '8359'))
pubTopic = GLOB.get_ini_value(setupFileName, 'MQTT', 'pub_topic', 'test') + userId + '/' + deviceId

# DHT11 센서 데이터 읽기
def read_dht11(sensor, pin):
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        return {
            "humidity": humidity,
            "temperature": temperature
        }
    else:
        print("Failed to retrieve data from humidity sensor")
        return None

def read_control():
    #todo ../bin/control.ini 파일 읽기
    #todo [CONTROL] 섹션 읽어서 딕셔너리로 반환
    control_list = GLOB.get_ini_section(setupFileName, 'CONTROL')
    # 리스트를 딕셔너리로 변환
    control_data = dict(control_list) if control_list else {}
    return control_data

def make_control_message(motor_id, control_data, current_temp, high_temp, low_temp):
    control_message = {}
    subTopic = GLOB.get_ini_value(setupFileName, 'MQTT', 'sub_topic', 'test') + userId + '/' + motor_id
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
def dht11_loop():
    while True:
        sensor_data = read_dht11(dht11_sensor, dht11_pin)
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
            GLOB.mqtt_publish(mqttUrl, mqttPort, pubTopic, combined_data)
            print("서버로 전송 완료")

            # 온도 제어 로직
            current_temp = sensor_data['temperature']
            high_temp = float(control_data.get('high', 0))
            low_temp = float(control_data.get('low', 0))
            status = control_data.get('status', 'off').lower()

            # status가 'on'일 때만 제어 실행
            if status == 'on':
                motor_id = GLOB.get_ini_value(setupFileName, 'AGENT', 'motor_id', 'motor01,motor02')

                for motor in motor_id.split(','):
                    subTopic, control_message = make_control_message(motor, control_data, current_temp, high_temp, low_temp)
                    print(f"제어 메시지: {control_message} 전송 주소: {subTopic}")
                    GLOB.mqtt_publish(mqttUrl, mqttPort, subTopic, control_message)
            else:
                print("제어 상태가 'off'입니다. 제어를 실행하지 않습니다.")
            
        else:
            print("센서 데이터를 읽을 수 없습니다. 10초 후 재시도합니다.")

        time.sleep(10)

if __name__ == '__main__':
    dht11_loop()