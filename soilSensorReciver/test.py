import time
import json
from pymodbus.client import ModbusSerialClient
from datetime import datetime
from frogmon.uGlobal import GLOB

# Modbus 설정
modbus_port = '/dev/ttyAMA0'  # 라즈베리 파이에 연결된 Modbus 포트
client = ModbusSerialClient(port=modbus_port, baudrate=9600, timeout=1)

# 현재 날짜와 CSV 파일명 설정
currentDate = datetime.now().strftime("%Y%m%d")
csvFileName = '/home/pi/FARMs_raspi_kit/csv/soildata_'
setupFileName = '/home/pi/FARMs_raspi_kit/bin/setup.ini'

# 설정 파일에서 MQTT 정보 읽기
userId = GLOB.get_ini_value(setupFileName, 'SETUP', 'user_id', 'test')
deviceId = GLOB.get_ini_value(setupFileName, 'AGENT', 'id', 'test')

mqttUrl = GLOB.get_ini_value(setupFileName, 'MQTT', 'url', 'frogmon.synology.me')
mqttPort = int(GLOB.get_ini_value(setupFileName, 'MQTT', 'port', '8359'))
pubTopic = GLOB.get_ini_value(setupFileName, 'MQTT', 'pub_topic', 'test') + userId + '/' + deviceId

# 데이터 요청 함수 (첫 번째 코드의 구조 적용)
def get_sensor_data():
    if client.connect():
        # Modbus 데이터를 요청하여 7개의 레지스터 값 읽기
        response = client.read_holding_registers(0x0000, 7)
        
        if not response.isError():
            # 읽은 데이터를 배열에 저장
            data = [
                response.getRegister(0),  # Humidity
                response.getRegister(1),  # Temperature
                response.getRegister(2),  # Conductivity
                response.getRegister(3),  # pH
                response.getRegister(4),  # Nitrogen
                response.getRegister(5),  # Phosphorus
                response.getRegister(6)   # Potassium
            ]
            return data
        else:
            print("센서 데이터 읽기 실패")
            return None
    else:
        print("Modbus 클라이언트 연결 실패")
        return None

# 센서 데이터 해석 (첫 번째 코드의 파싱 방식 적용)
def parse_sensor_data(data):
    if data:
        sensor_data = {
            "humidity": data[0] * 0.1,
            "temperature": data[1] * 0.1,
            "conductivity": data[2],
            "PH": data[3] * 0.1,
            "nitrogen": data[4],
            "phosphorus": data[5],
            "potassium": data[6]
        }
        return sensor_data
    else:
        return None

# 데이터 출력 및 저장 루프
def print_loop():
    while True:
        currentDate = datetime.now().strftime("%Y%m%d")
        raw_data = get_sensor_data()
        
        if raw_data:
            sensor_data = parse_sensor_data(raw_data)
            if sensor_data:
                print("센서 데이터:")
                print(sensor_data)
                
                # CSV에 데이터 저장
                GLOB.save_sensor_data_to_csv(csvFileName + currentDate + '.csv', sensor_data)
                print("센서 데이터가 저장되었습니다.")
                
                # MQTT 서버로 데이터 전송
                GLOB.mqtt_publish(mqttUrl, mqttPort, pubTopic, sensor_data)
                print("센서 데이터를 서버로 전송")
                
        time.sleep(10)

if __name__ == '__main__':
    print_loop()
