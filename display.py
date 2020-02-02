import time

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
from PIL import Image
import re
import time


class DisplayDriver():

    def __init__(self):
        block_orientation = -90
        rotate = 0
        inreverse = False
        width = 64
        height = 16
        self.serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(self.serial, block_orientation=block_orientation,
                     rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse,
                     width=width, height=height)

    def show_image(self, path, x, y):
        with canvas(self.device) as draw:
            draw.point([0,8,1,9,2,10,3,11,4,12], fill="white")
            

    def write_first_line(self, data):
        with canvas(self.device) as draw:
            text(draw, (0, 0), data, fill="white", font=proportional(TINY_FONT))

    def write_second_line(self, data):
        with canvas(self.device) as draw:
            text(draw, (0, 8), data, fill="white", font=proportional(LCD_FONT))
