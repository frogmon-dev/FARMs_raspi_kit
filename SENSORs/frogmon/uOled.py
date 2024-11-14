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

    def display_sensor_data(self, data):
        """
        센서 데이터를 OLED에 예쁘게 표시하는 함수
        :param data: 센서 데이터 딕셔너리 (예: {"temperature": 22.5, "humidity": 60.0, ...})
        """
        if not self.border_drawn:
            self.draw_border()

        with canvas(self.device) as draw:
            # 테두리 유지
            padding = 2
            draw.rectangle(
                (padding, padding, self.device.width - padding, self.device.height - padding),
                outline="white",
                fill="black"
            )

            # 폰트 설정
            label_font = ImageFont.truetype(self.default_font_path, 10)  # 작은 폰트
            value_font = ImageFont.truetype(self.default_font_path, 12)  # 큰 폰트

            # 위치 설정 및 데이터 표시
            draw.text((5, 5), "Temp:", font=label_font, fill="white")
            draw.text((45, 5), f"{data['temperature']}/{data['out_temperature']} C", font=value_font, fill="white")

            draw.text((5, 20), "Humi:", font=label_font, fill="white")
            draw.text((45, 20), f"{data['humidity']}/{data['out_humidity']} %", font=value_font, fill="white")

            draw.text((5, 35), "Cond:", font=label_font, fill="white")
            draw.text((45, 35), f"{data['conductivity']}", font=value_font, fill="white")
            
            draw.text((70, 35), "PH:", font=label_font, fill="white")
            draw.text((95, 35), f"{data['PH']}", font=value_font, fill="white")
            
            draw.text((5, 50), "N:", font=label_font, fill="white")
            draw.text((25, 50), f"{data['nitrogen']}", font=value_font, fill="white")
            
            draw.text((45, 50), "P:", font=label_font, fill="white")
            draw.text((60, 50), f"{data['phosphorus']}", font=value_font, fill="white")
            
            draw.text((90, 50), "K:", font=label_font, fill="white")
            draw.text((105, 50), f"{data['potassium']}", font=value_font, fill="white")
            

            # 추가 데이터도 필요한 경우 배치 가능
            # draw.text((x, y), "Label", font=label_font, fill="white")
            # draw.text((x_offset, y), f"{value}", font=value_font, fill="white")