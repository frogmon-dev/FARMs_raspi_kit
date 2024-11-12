from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
import time

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, rotate=1)

# Box and text rendered in portrait mode
with canvas(device) as draw:
    padding = 2
    draw.rectangle(
        (padding, padding, device.width - padding, device.height - padding),
        outline="white",
        fill="black"
    )
    draw.text((20, 20), "Hello World!", fill="white")
while 1:
    time.sleep(1)
    