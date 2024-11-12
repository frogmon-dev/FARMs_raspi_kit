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
        self.display_content = []  # 화면에 출력할 내용을 저장
        self.border_drawn = False  # 테두리가 그려졌는지 여부를 추적
        
        padding = 2
        with canvas(self.device) as draw:
            draw.rectangle(
                (padding, padding, self.device.width - padding, self.device.height - padding),
                outline="white",
                fill="black"
            )
            
    def draw_border(self):
        """
        테두리를 한 번만 그리도록 하는 함수
        """
        padding = 2
        with canvas(self.device) as draw:
            draw.rectangle(
                (padding, padding, self.device.width - padding, self.device.height - padding),
                outline="white",
                fill="black"
            )
        self.border_drawn = True            

    def display_test(self, x, y, text, size):
        """
        텍스트를 추가할 때 화면 테두리가 유지되도록 출력
        """
        # 테두리가 없으면 한 번만 그리기
        if not self.border_drawn:
            self.draw_border()

        # 새 텍스트를 저장하고 화면에 업데이트
        self.display_content.append((x, y, text, size))
        with canvas(self.device) as draw:
            # 테두리를 다시 그려주기
            padding = 2
            draw.rectangle(
                (padding, padding, self.device.width - padding, self.device.height - padding),
                outline="white",
                fill="black"
            )
            
            # 저장된 모든 텍스트 그리기
            for x, y, text, size in self.display_content:
                font = ImageFont.truetype(self.default_font_path, size)
                draw.text((x, y), text, font=font, fill="white")
