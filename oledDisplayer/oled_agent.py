from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
import time

# I2C 설정
serial = i2c(port=1, address=0x3C)
# 디스플레이를 세로 모드로 설정 (rotate=1 또는 3 사용)
device = ssd1306(serial, rotate=1)

# 글꼴 설정 (크기를 키우기 위해 truetype 폰트 로드)
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # 경로에 적합한 글꼴 사용
font_size = 14  # 원하는 글씨 크기로 설정
font = ImageFont.truetype(font_path, font_size)

# 박스와 텍스트를 세로 모드에 맞게 렌더링
with canvas(device) as draw:
    # 여백을 준 직사각형
    padding = 2
    draw.rectangle(
        (padding, padding, device.width - padding, device.height - padding),
        outline="white",
        fill="black"
    )
    # 텍스트를 여백을 두고 아래로 약간 내림
    draw.text((padding + 2, padding + 2), "Hello World!", fill="white", font=font)

while True:
    time.sleep(1)