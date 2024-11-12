import time
from pymodbus.client import ModbusSerialClient  # 최신 구조에 맞게 수정

# Modbus Serial Client 설정
modbus_port = '/dev/ttyAMA0'  # 라즈베리 파이의 UART 포트
client = ModbusSerialClient(method='rtu', port=modbus_port, baudrate=9600, timeout=1)

# Modbus 명령어 설정 (아두이노 코드에서 사용한 명령어와 동일하게 설정)
commands = {
    'temperature': [0x01, 0x03, 0x00, 0x13, 0x00, 0x01, 0x75, 0xcf],
    'moisture': [0x01, 0x03, 0x00, 0x12, 0x00, 0x01, 0x24, 0x0F],
    'conductivity': [0x01, 0x03, 0x00, 0x15, 0x00, 0x01, 0x95, 0xce],
    'ph': [0x01, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x0b],
    'nitrogen': [0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C],
    'phosphorus': [0x01, 0x03, 0x00, 0x1f, 0x00, 0x01, 0xb5, 0xcc],
    'potassium': [0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xc0],
}

def send_modbus_command(command):
    # Modbus 명령을 전송
    client.write_registers(0, command)

    # 응답 읽기
    response = client.read_holding_registers(0, 7)  # 예상 응답 길이 = 7 바이트
    if response.isError():
        print("센서 데이터 읽기 실패")
        return None
    else:
        return response.registers

def parse_response(response):
    # 유효한 응답인지 확인
    if response and len(response) >= 4:
        return response[3] << 8 | response[4]  # 데이터 바이트를 합쳐서 반환
    return None

def read_sensor_data():
    data = {}

    # 수분도
    response = send_modbus_command(commands['moisture'])
    data['Moisture'] = parse_response(response) / 10.0 if response else None
    time.sleep(1)

    # 온도
    response = send_modbus_command(commands['temperature'])
    data['Temperature'] = parse_response(response) / 10.0 if response else None
    time.sleep(1)

    # 전도도
    response = send_modbus_command(commands['conductivity'])
    data['Conductivity'] = parse_response(response) if response else None
    time.sleep(1)

    # pH
    response = send_modbus_command(commands['ph'])
    data['pH'] = parse_response(response) / 10.0 if response else None
    time.sleep(1)

    # 질소
    response = send_modbus_command(commands['nitrogen'])
    data['Nitrogen'] = parse_response(response) if response else None
    time.sleep(1)

    # 인
    response = send_modbus_command(commands['phosphorus'])
    data['Phosphorus'] = parse_response(response) if response else None
    time.sleep(1)

    # 칼륨
    response = send_modbus_command(commands['potassium'])
    data['Potassium'] = parse_response(response) if response else None
    time.sleep(1)

    return data

if __name__ == '__main__':
    try:
        client.connect()
        while True:
            sensor_data = read_sensor_data()
            if sensor_data:
                print("센서 데이터:", sensor_data)
            time.sleep(10)
    except KeyboardInterrupt:
        print("프로그램 종료")
    finally:
        client.close()
