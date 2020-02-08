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
from helper import make_string_from_list, get_width, get_image_as_list
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
        start = datetime.time(21, 00) # + eine Stunde rechnen für richtige Zeit (schaltet um 22 Uhr um)
        end = datetime.time(6, 30)
        timestamp = datetime.datetime.now().time()
        if True or timestamp < end and timestamp > start: # TODO: Automatic switching doesnt work
            print("dark")
            self.device.contrast(0x0)
        else:
            print("bright")
            self.device.contrast(0x60)

    def display_minutes(self, draw, minutes, cache, x, y):
        animate = False
        if not (minutes == cache):
            if (len(cache) != 0 and len(minutes) != 0 and 
                (cache[0]["minutes"] < minutes[0]["minutes"] and 
                cache["minutes"] < 2 and
                minutes[0]["minutes"] < 5)):
                animate = True

        soonest_bahn = True
        for departure in minutes:
            minute = departure["minutes"]
            width = get_width(minute)
            if soonest_bahn and animate:
                pass
                soonest_bahn = False
            #print(str(minute) + ": " + str(x) + "/" + str(y))
            text(draw, (x, y), str(minute),
                fill="white", font=proportional(LCD_FONT))
            x += width + 1
            draw.point([x, y+5, x, y+6], fill="white")
            text(draw, (x, y), " ",
                    fill="white", font=proportional(LCD_FONT))
            x += 2
        draw.point([x-3, y, x-2, y, x-3, y+1, x-2, y+1, x-3, y+2, 
                   x-2, y+2, x-3, y+3, x-2, y+3, x-3, y+4, x-2, y+4, 
                   x-3, y+5, x-2, y+5, x-3, y+6, x-2, y+6], fill="black")
        text(draw, (x-3, y), "  ",
                    fill="white", font=proportional(LCD_FONT))
                
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
                draw.point(get_image_as_list(
                    "icons/city.txt", 0, 0), fill="white")
                draw.point(get_image_as_list(
                    "icons/airplane.txt", 0, 8), fill="white")
                #text(draw, (9, 0), make_string_from_list(s8_herrsching_minutes),
                #     fill="white", font=proportional(LCD_FONT))
                self.display_minutes(draw, s8_herrsching_minutes, self.s8_herrsching_minutes_cache, 9, 0)
                for s8_flughafen_minute in s8_flughafen_minutes:
                    text(draw, (9, 8), make_string_from_list(s8_flughafen_minutes),
                        fill="white", font=proportional(LCD_FONT))

    def write_first_line(self, data):
        with canvas(self.device) as draw:
            text(draw, (0, 0), data, fill="white", font=proportional(TINY_FONT))

    def write_second_line(self, data):
        with canvas(self.device) as draw:
            text(draw, (0, 8), data, fill="white", font=proportional(LCD_FONT))
