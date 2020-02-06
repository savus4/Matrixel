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
from helper import make_string_from_list
import datetime


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
        self.device.contrast(0x10)
        self.s8_flughafen_minutes_cache = list()
        self.s8_herrsching_minutes_cache = list()

    def set_brightness(self):
        start = datetime.time(21, 00)
        end = datetime.time(22, 42)
        timestamp = datetime.datetime.now().time()
        if timestamp < end and timestamp > start:
            print("dark")
            self.device.contrast(0x0)
        else:
            print("bright")
            self.device.contrast(0xA0)

    def s_bahn_layout(self, s8_flughafen_minutes, s8_herrsching_minutes):
        self.set_brightness()
        print(str(s8_flughafen_minutes))
        if not ((s8_flughafen_minutes == self.s8_flughafen_minutes_cache) and
                s8_herrsching_minutes == self.s8_herrsching_minutes_cache):
            if (len(self.s8_flughafen_minutes_cache) != 0 and len(s8_flughafen_minutes) != 0 and 
                (self.s8_flughafen_minutes_cache[0]["minutes"] < s8_flughafen_minutes[0]["minutes"] and 
                self.s8_flughafen_minutes_cache[0]["minutes"] < 2 and
                s8_flughafen_minutes[0]["minutes"] < 5)):
                animate_flughafen = True
            else:
                animate_flughafen = False
            self.s8_flughafen_minutes_cache = s8_flughafen_minutes
            self.s8_herrsching_minutes_cache = s8_herrsching_minutes
            with canvas(self.device) as draw:
                draw.point(self.get_image_as_list(
                    "icons/city.txt", 0, 0), fill="white")
                draw.point(self.get_image_as_list(
                    "icons/airplane.txt", 0, 8), fill="white")
                text(draw, (9, 0), make_string_from_list(s8_herrsching_minutes),
                     fill="white", font=proportional(LCD_FONT))
                for s8_flughafen_minute in s8_flughafen_minutes:
                    text(draw, (9, 8), make_string_from_list(s8_flughafen_minutes),
                        fill="white", font=proportional(LCD_FONT))

    def get_image_as_list(self, path, offset_x, offset_y):
        display_list = list()
        with open(path) as picture:
            line = picture.readline()
            x = offset_x
            y = offset_y
            while line:
                line = line.strip()
                for char in line:
                    if char == "*":
                        display_list.append(x)
                        display_list.append(y)
                    x += 1
                line = picture.readline()
                x = offset_x
                y += 1
        return display_list

    def write_first_line(self, data):
        with canvas(self.device) as draw:
            text(draw, (0, 0), data, fill="white", font=proportional(TINY_FONT))

    def write_second_line(self, data):
        with canvas(self.device) as draw:
            text(draw, (0, 8), data, fill="white", font=proportional(LCD_FONT))
