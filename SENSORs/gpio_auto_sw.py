import time
import json
from datetime import datetime
import RPi.GPIO as GPIO
from frogmon.uGlobal import GLOB

# 설정 파일 경로
setupFileName = '/home/pi/FARMs_raspi_kit/bin/setup.ini'

# GPIO 설정
SWITCH_PIN = 26  # 스위치가 연결된 GPIO 핀

def setup_gpio():
    """GPIO 설정 초기화"""
    GPIO.setmode(GPIO.BCM)  # BCM 모드 사용
    GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 내부 풀업 저항 사용
    print(f"GPIO {SWITCH_PIN} 핀을 입력으로 설정했습니다.")

def read_switch():
    """스위치 상태 읽기"""
    try:
        # 스위치 상태 읽기 (HIGH=off, LOW=on)
        switch_state = GPIO.input(SWITCH_PIN)
        
        # 스위치가 연결된 핀이 LOW일 때 on, HIGH일 때 off
        if switch_state == GPIO.LOW:
            return "on"
        else:
            return "off"
    except Exception as e:
        print(f"스위치 읽기 오류: {e}")
        return "error"

def main():
    print("GPIO 스위치 모니터링 시작")
    print(f"스위치 핀: GPIO {SWITCH_PIN}")
    
    try:
        # GPIO 설정
        setup_gpio()
        
        # 이전 상태 저장
        previous_state = None
        
        while True:
            # 현재 스위치 상태 읽기
            current_state = read_switch()
            
            # 상태가 변경되었을 때만 출력
            if current_state != previous_state:
                print(f"스위치 상태: {current_state}")
                previous_state = current_state

                if current_state == "on":
                    print("스위치가 켜졌습니다.")
                    GLOB.set_ini_value(setupFileName, 'CONTROL', 'status', 'on')
                else:
                    print("스위치가 꺼졌습니다.")
                    GLOB.set_ini_value(setupFileName, 'CONTROL', 'status', 'off')
            
            # 0.1초 대기
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n프로그램 종료")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
    finally:
        # GPIO 정리
        GPIO.cleanup()
        print("GPIO 정리 완료")

if __name__ == '__main__':
    main()


