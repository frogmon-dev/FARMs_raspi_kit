import time
import json
from pymodbus.client import ModbusSerialClient
import RPi.GPIO as GPIO
from datetime import datetime
import Adafruit_DHT
import struct

from frogmon.uGlobal     import GLOB
from frogmon.uOled       import UOled

# 센서 타입과 연결 핀을 설정합니다.
dht11_sensor = Adafruit_DHT.DHT11
dht11_pin = 10  # DHT11 센서의 데이터 핀이 연결된 GPIO 핀 번호

# Modbus 설정
modbus_port = '/dev/ttyAMA0'  # 라즈베리 파이에 연결된 Modbus 포트
client = ModbusSerialClient(port=modbus_port, baudrate=4800, timeout=1)

currentDate = datetime.now().strftime("%Y%m%d")
csvFileName = '/home/pi/FARMs_raspi_kit/csv/soildata_'
setupFileName = '/home/pi/FARMs_raspi_kit/bin/setup.ini'

userId = GLOB.get_ini_value(setupFileName, 'SETUP', 'user_id', 'test')
deviceId = GLOB.get_ini_value(setupFileName, 'AGENT', 'id', 'test')

mqttUrl  = GLOB.get_ini_value(setupFileName, 'MQTT', 'url', 'frogmon.synology.me')
mqttPort = int(GLOB.get_ini_value(setupFileName, 'MQTT', 'port', '8359'))
pubTopic = GLOB.get_ini_value(setupFileName, 'MQTT', 'pub_topic', 'test')+userId+'/'+deviceId

oled = UOled(rotate=0)
oled.display_test(10, 10, "Hello OLED!", 10)

# 요청 패킷 (7-in-1 센서)
#p7in1_request = [0x01, 0x03, 0x00, 0x00, 0x00, 0x07, 0x04, 0x08]
p7in1_request = [0x01, 0x03, 0x00, 0x12, 0x00, 0x02, 0x64, 0x0E]

# 센서 데이터를 읽어오는 함수
def read_dht11(sensor, pin):
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        print(f"Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
        return temperature, humidity 
    else:
        print("Failed to retrieve data from humidity sensor")        



# 데이터 요청 함수
def get_sensor_data():
    if client.connect():
        # 요청 패킷 전송
        client.write_registers(0, p7in1_request)
        time.sleep(0.2)

        # 19바이트 데이터 읽기
        response = client.read_holding_registers(0, 19)
        if response.isError():
            print("센서 데이터 읽기 실패")
            return None
        else:
            return response.encode()  # 바이트 배열로 반환
    else:
        print("Modbus 클라이언트 연결 실패")
        return None

# 센서 데이터 해석
def parse_sensor_data(data):
    if len(data) < 19:
        print("데이터가 부족합니다.")
        return None

    # 센서 값 추출
    temperature = struct.unpack('>h', data[3:5])[0] / 10.0
    humidity = struct.unpack('>H', data[5:7])[0] / 10.0
    conductivity =  struct.unpack('>H', data[7:9])[0]
    ph =  struct.unpack('>H', data[9:11])[0] / 100.0 
    nitrogen = struct.unpack('>H', data[11:13])[0] 
    phosphorus = struct.unpack('>H', data[13:15])[0]
    potassium = struct.unpack('>H', data[15:17])[0]  

    sensor_data = {
        "humidity": humidity,
        "temperature": temperature,
        "conductivity": conductivity,
        "PH": ph,
        "nitrogen": nitrogen,
        "phosphorus": phosphorus,
        "potassium": potassium
    }
    return sensor_data
    #return json.dumps(sensor_data, indent=2)

# 데이터 출력 루프
def print_loop():
    while True:
        currentDate = datetime.now().strftime("%Y%m%d")
        raw_data = get_sensor_data()
        if raw_data:
            sensor_data = parse_sensor_data(raw_data)
            if sensor_data:
                temp, humi = read_dht11(dht11_sensor, dht11_pin)

                # Add out_temperature and out_humidity if they are available
                if temp is not None and humi is not None:
                    sensor_data["out_temperature"] = temp
                    sensor_data["out_humidity"] = humi

                print("센서 데이터:")
                print(sensor_data)
                
                oled.display_sensor_data(sensor_data)
                
                GLOB.save_sensor_data_to_csv(csvFileName + currentDate + '.csv', sensor_data)                    
                print("센서 데이터가 저장되었습니다.")
                
                GLOB.mqtt_publish(mqttUrl, mqttPort, pubTopic, sensor_data)
                print("센서 데이터를 서버로 전송")
                
        time.sleep(10)

if __name__ == '__main__':
    print_loop()