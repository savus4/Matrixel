import time
import os
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
from datetime import datetime, timedelta
from datetime import time as dtTime


class DisplayDriver():

    def __init__(self, msg_manager, startup_screen=True):
        block_orientation = -90
        rotate = 0
        inreverse = False
        width = 64
        height = 16
        self.serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(self.serial, block_orientation=block_orientation,
                              rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse,
                              width=width, height=height)
        self.device.contrast(0xFF)
        if startup_screen:
            self.start_up_screen()
        self.s8_flughafen_minutes_cache = list()
        self.s8_herrsching_minutes_cache = list()
        self.minute_cache = 0
        self.seconds_cache = 0
        self.number_next_connections = 3
        self.refresh_counter = 0
        self.last_refresh_cache = datetime.now()
        self.is_sleeping = False
        self.sleep_wait_counter = 0
        self.sleeping_file = "sleeping.txt"
        self.msg_manager = msg_manager


    def set_brightness(self):
        now_time = datetime.utcnow().time()
        if now_time >= dtTime(17, 30) or now_time <= dtTime(6, 30):
            self.device.contrast(0xFF)
        else:
            self.device.contrast(0xFF)

    def start_up_screen(self, display_time=2):
        with canvas(self.device) as draw:
                text(draw, (0, 4), "Dagl-Info",
                    fill="white", font=proportional(CP437_FONT))
        time.sleep(display_time)


    def display_minutes(self, draw, minutes, cache, x, y):
        animate = False
        # if not (minutes == cache):
        #     if (len(cache) != 0 and len(minutes) != 0 and 
        #         (cache[0]["minutes"] < minutes[0]["minutes"] and 
        #         cache["minutes"] < 2 and
        #         minutes[0]["minutes"] < 5)):
        #         animate = True

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

    def get_next_connections_excerpt(self, min_list):
        if len(min_list) >= self.number_next_connections:
            return min_list[0:self.number_next_connections]
        else:
            return min_list


    def check_animation(self, direction):
        '''
        Not working yet. Only extracted out of ´main_layout´ to clear things up.
        '''
        if (len(self.s8_flughafen_minutes_cache) != 0 and len(s8_flughafen_minutes) != 0 and 
                    (self.s8_flughafen_minutes_cache[0]["minutes"] < s8_flughafen_minutes[0]["minutes"] and 
                    self.s8_flughafen_minutes_cache[0]["minutes"] < 2 and
                    s8_flughafen_minutes[0]["minutes"] < 5)):
                    animate_flughafen = True
        else:
            animate_flughafen = False
        return animate_flughafen

    def in_sleep_mode(self):
        # auto wake up in the morning
        now_time = datetime.now().time()
        if now_time >= dtTime(5, 50, 0) and now_time <= dtTime(5, 50, 3):
            print("must wake up")
            self.wake_up()
            return False
        # don't check file too often
        if self.sleep_wait_counter < 10:
            self.sleep_wait_counter += 1
            return self.is_sleeping
        else:
            self.sleep_wait_counter = 0
        # check if file exists
        if os.path.exists(self.sleeping_file) and os.path.isfile(self.sleeping_file):
            return True
        # wake up if sleeping at the moment
        elif self.is_sleeping:
            self.wake_up()
            return False

    def wake_up(self):
        if os.path.exists(self.sleeping_file) and os.path.isfile(self.sleeping_file):
            os.remove(self.sleeping_file)
        self.s8_flughafen_minutes_cache = None
        self.s8_herrsching_minutes_cache = None
        self.is_sleeping = False
                
    def sleep_screen(self):
        if not self.is_sleeping:
            self.device.contrast(0xFF)
            sleep_file = "/home/pi/Documents/mvg_departure_monitor/icons/moon.txt"
            with canvas(self.device) as draw:
                if os.path.exists(sleep_file) and os.path.isfile(sleep_file):
                    draw.point(get_image_as_list(
                               "/home/pi/Documents/mvg_departure_monitor/icons/moon.txt", 55, 2), fill="white")
                else:
                    draw.point([63, 0], fill="white")
            self.is_sleeping = True

    def toggle_sleep_mode(self):
        if self.is_sleeping:
            print("waking up")
            self.wake_up()
            return "awaking"
        else:
            print("going to sleep")
            self.sleep_screen()
            return "sleeping"


    def show_idle_state(self, scraper):
        #successfull_refresh = self.check_refresh(scraper.last_refresh)
        minutes_since_last_refresh = None
        if scraper.last_refresh:
            minutes_since_last_refresh = datetime.now() - scraper.last_refresh
        #if minutes_since_last_refresh:
        #   print("minutes since last refresh: " + str(minutes_since_last_refresh) + 
        #       "\nrefresh_counter: " + str(self.refresh_counter))
        if minutes_since_last_refresh and minutes_since_last_refresh < timedelta(minutes=3):
            self.reset_refresh_counter_at(30*10)
            if self.refresh_counter == 0:
                with canvas(self.device) as draw:
                    draw.point([0, 0], fill="black")
            elif self.refresh_counter == 6 :
                with canvas(self.device) as draw:
                    draw.point([0, 0], fill="white")
        elif not minutes_since_last_refresh or minutes_since_last_refresh > timedelta(minutes=3):
            self.reset_refresh_counter_at(10)
            if self.refresh_counter == 0:
                with canvas(self.device) as draw:
                    draw.point([0, 0], fill="black")
            elif self.refresh_counter == 6 :
                with canvas(self.device) as draw:
                    draw.point([0, 0], fill="white")
        else:
            with canvas(self.device) as draw:
                draw.point([0, 0], fill="white")
        self.refresh_counter += 1

    def reset_refresh_counter_at(self, number):
        if self.refresh_counter >= number:
            self.refresh_counter = 0

    def check_refresh(self, last_refresh):
        if not last_refresh:
            return False
        refresh_successfull = last_refresh != self.last_refresh_cache
        self.last_refresh_cache = last_refresh
        return refresh_successfull

    def draw_city_line(self, draw, s8_herrsching_minutes):
        draw.point(get_image_as_list(
            "/home/pi/Documents/mvg_departure_monitor/icons/frauenkirche.txt", 0, 0), fill="white")
        self.display_minutes(draw, s8_herrsching_minutes, self.s8_herrsching_minutes_cache, 9, 0)


    def draw_airport_line(self, draw, s8_flughafen_minutes):
        draw.point(get_image_as_list(
            "/home/pi/Documents/mvg_departure_monitor/icons/airplane.txt", 0, 8), fill="white")
        self.display_minutes(draw, s8_flughafen_minutes, self.s8_flughafen_minutes_cache, 9, 9)


    def check_as_usual(self, lines, number_departures=3):
        as_usual = True
        for departures in lines:
            i = 0
            for departure in departures:     
                if i < number_departures and not departure["as_usual"]:
                    as_usual = False
                i = i + 1
        return as_usual

    def write_first_line(self, data):
        with canvas(self.device) as draw:
            text(draw, (0, 0), data, fill="white", font=proportional(TINY_FONT))

    def write_second_line(self, data):
        with canvas(self.device) as draw:
            text(draw, (0, 8), data, fill="white", font=proportional(LCD_FONT))

    def main_layout(self, scraper, message=None):
        if self.in_sleep_mode():
            self.sleep_screen()
            return
        s8_flughafen_minutes = self.get_next_connections_excerpt(scraper.s8_airport_min_list)
        s8_herrsching_minutes = self.get_next_connections_excerpt(scraper.s8_city_min_list)
        if not self.check_as_usual([s8_flughafen_minutes, s8_herrsching_minutes]):
            if not ((s8_flughafen_minutes == self.s8_flughafen_minutes_cache) and
                    s8_herrsching_minutes == self.s8_herrsching_minutes_cache):
                self.set_brightness()
                self.refresh_counter = 0
                self.s8_flughafen_minutes_cache = s8_flughafen_minutes
                self.s8_herrsching_minutes_cache = s8_herrsching_minutes
                with canvas(self.device) as draw:
                    self.draw_city_line(draw, s8_herrsching_minutes)
                    self.draw_airport_line(draw, s8_flughafen_minutes)
        elif self.msg_manager.has_current_message():
            self.set_brightness()
            self.refresh_counter = 0
            self.message_counter += 1
            with canvas(self.device) as draw:
                text(draw, (16, 0), datetime.now().strftime("%H:%M"),
                    fill="white", font=proportional(CP437_FONT))
                try:
                    text(draw, (0, 9), message[:-1],
                        fill="white", font=proportional(LCD_FONT))
                except IndexError as e:
                    pass
        else:
            self.device.contrast(0xFF)
            self.show_idle_state(scraper)