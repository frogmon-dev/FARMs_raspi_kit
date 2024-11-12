import time
import serial
import RPi.GPIO as GPIO

# RS-485 제어 핀 설정
RE_PIN = 6
DE_PIN = 7

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(RE_PIN, GPIO.OUT)
GPIO.setup(DE_PIN, GPIO.OUT)

# 초기 송신 모드 비활성화
GPIO.output(DE_PIN, GPIO.LOW)
GPIO.output(RE_PIN, GPIO.LOW)

# Serial 포트 설정
serial_port = serial.Serial(
    port='/dev/ttyAMA0',  # 연결된 포트
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

# 센서 명령
temp = [0x01, 0x03, 0x00, 0x13, 0x00, 0x01, 0x75, 0xcf]
mois = [0x01, 0x03, 0x00, 0x12, 0x00, 0x01, 0x24, 0x0F]
econ = [0x01, 0x03, 0x00, 0x15, 0x00, 0x01, 0x95, 0xce]
ph = [0x01, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x0b]
nitro = [0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C]
phos = [0x01, 0x03, 0x00, 0x1f, 0x00, 0x01, 0xb5, 0xcc]
pota = [0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xc0]

def send_request(command):
    # 송신 모드 활성화
    GPIO.output(DE_PIN, GPIO.HIGH)
    GPIO.output(RE_PIN, GPIO.HIGH)
    time.sleep(0.01)

    # 명령 전송
    serial_port.write(bytearray(command))
    serial_port.flush()

    # 수신 모드로 전환
    GPIO.output(DE_PIN, GPIO.LOW)
    GPIO.output(RE_PIN, GPIO.LOW)
    time.sleep(0.2)

    # 응답 읽기
    response = serial_port.read(7)
    return response

def parse_response(response):
    if len(response) == 7:
        # 센서 데이터 값이 응답의 4번째 바이트에 위치
        return response[3] << 8 | response[4]
    return None

def get_sensor_data():
    data = {}
    
    # 수분도 데이터 수집
    response = send_request(mois)
    data['Moisture'] = parse_response(response) / 10.0 if response else None
    time.sleep(1)
    
    # 온도 데이터 수집
    response = send_request(temp)
    data['Temperature'] = parse_response(response) / 10.0 if response else None
    time.sleep(1)

    # 전도도 데이터 수집
    response = send_request(econ)
    data['Conductivity'] = parse_response(response) if response else None
    time.sleep(1)

    # pH 데이터 수집
    response = send_request(ph)
    data['pH'] = parse_response(response) / 10.0 if response else None
    time.sleep(1)

    # 질소 데이터 수집
    response = send_request(nitro)
    data['Nitrogen'] = parse_response(response) if response else None
    time.sleep(1)

    # 인 데이터 수집
    response = send_request(phos)
    data['Phosphorus'] = parse_response(response) if response else None
    time.sleep(1)

    # 칼륨 데이터 수집
    response = send_request(pota)
    data['Potassium'] = parse_response(response) if response else None
    time.sleep(1)

    return data

if __name__ == '__main__':
    try:
        while True:
            sensor_data = get_sensor_data()
            if sensor_data:
                print("센서 데이터:", sensor_data)
            time.sleep(10)
    except KeyboardInterrupt:
        print("프로그램 종료")
    finally:
        GPIO.cleanup()
        serial_port.close()
