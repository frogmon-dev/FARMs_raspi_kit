import time
import json
from pymodbus.client import ModbusSerialClient
import RPi.GPIO as GPIO
import csv
import os
from datetime import datetime


# Modbus 설정
modbus_port = '/dev/ttyAMA0'  # 라즈베리 파이에 연결된 Modbus 포트
client = ModbusSerialClient(port=modbus_port, baudrate=4800, timeout=1)

currentDate = datetime.now().strftime("%Y%m%d")
csvFileName = '/home/pi/SOILs/bin/csv/soildata_'

# 요청 패킷 (7-in-1 센서)
p7in1_request = [0x01, 0x03, 0x00, 0x00, 0x00, 0x07, 0x04, 0x08]

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
    humidity = (data[3] << 8 | data[4]) / 10.0
    temperature = (data[5] << 8 | data[6]) / 10.0
    conductivity = data[7] << 8 | data[8]
    ph = (data[9] << 8 | data[10]) / 10.0
    nitrogen = data[11] << 8 | data[12]
    phosphorus = data[13] << 8 | data[14]
    potassium = data[15] << 8 | data[16]

    sensor_data = {
        "humidity": humidity,
        "temperature": temperature,
        "conductivity": conductivity,
        "PH": ph,
        "nitrogen": nitrogen,
        "phosphorus": phosphorus,
        "potassium": potassium
    }

    return json.dumps(sensor_data, indent=2)

# 데이터 출력 루프
def print_loop():
    while True:
        currentDate = datetime.now().strftime("%Y%m%d")
        raw_data = get_sensor_data()
        if raw_data:
            sensor_data = parse_sensor_data(raw_data)
            if sensor_data:
                print("센서 데이터:")                
                print(sensor_data)
                if isinstance(sensor_data, dict):
                    save_sensor_data_to_csv(csvFileName + currentDate + '.csv', sensor_data)
                    print("센서 데이터가 저장되었습니다.")
                else:
                    print("sensor_data가 딕셔너리가 아닙니다. 데이터 형식을 확인하세요.")                
                save_sensor_data_to_csv(csvFileName+currentDate+'.csv', sensor_data)
        time.sleep(10)

if __name__ == '__main__':
    print_loop()