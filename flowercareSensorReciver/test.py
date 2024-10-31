
import os

def get_current_path():
    # 현재 스크립트 파일의 위치를 기준으로 bin 디렉토리 경로를 설정
    return os.path.dirname(os.path.abspath(__file__))

print(get_current_path())