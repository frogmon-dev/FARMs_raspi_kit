from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont

class UOled:
    def __init__(self, address=0x3C, rotate=0):
        """
        OLED 초기화 및 회전 설정
        :param address: I2C 주소, 기본값 0x3C
        :param rotate: 화면 회전 (0, 1, 2, 3 중 하나)
        """
        self.serial = i2c(port=1, address=address)
        self.device = ssd1306(self.serial, rotate=rotate)
        self.default_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        padding = 2
        with canvas(self.device) as draw:
            draw.rectangle(
                (padding, padding, self.device.width - padding, self.device.height - padding),
                outline="white",
                fill="black"
            )

    def display_test(self, x, y, text, size):
        """
        OLED 화면에 텍스트를 출력
        :param x: 텍스트 시작 x 좌표
        :param y: 텍스트 시작 y 좌표
        :param text: 출력할 텍스트
        :param size: 텍스트의 폰트 크기
        """
        # 지정된 크기의 폰트 로드
        font = ImageFont.truetype(self.default_font_path, size)
        
        # 텍스트를 화면에 출력
        with canvas(self.device) as draw:
            draw.text((x, y), text, font=font, fill="white")

# 사용 예시
if __name__ == "__main__":
    oled = UOled(rotate=1)  # 예를 들어, 회전 90도 설정
    oled.display_test(10, 10, "Hello OLED!", 12)  # (10,10) 위치에 크기 12로 텍스트 출력
