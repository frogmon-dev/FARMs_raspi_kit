import Adafruit_DHT

# 센서 타입과 연결 핀을 설정합니다.
sensor = Adafruit_DHT.DHT11
pin = 2  # DHT11 센서의 데이터 핀이 연결된 GPIO 핀 번호

# 센서 데이터를 읽어오는 함수
def read_dht11():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        print(f"Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
    else:
        print("Failed to retrieve data from humidity sensor")

# 실행
if __name__ == "__main__":
    read_dht11()
