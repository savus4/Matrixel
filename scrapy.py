import requests
import threading
import sched
import json
import datetime as dt
from tabulate import tabulate
from math import floor
import pickle
import time
import logging
import os
from display import DisplayDriver
from helper import make_string_from_list, get_image_as_list

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT



logging.basicConfig(level=logging.DEBUG)

show_next_connections = 5
data_folder = "data/"
s8_into_city = ["Herrsching", "Weßling", "Gilching-Argelsried", "Pasing", "Ostbahnhof", "Leuchtenbergring"]
s8_into_city_warning = ["Ostbahnhof", "Leuchtenbergring", "Rosenheimer", "Isartor"]
s8_to_airport = ["Flughafen", "Ismaning", "Unterföhring"]
s8_to_airport_warning = ["Unterföhring"]

def fetch_data(url, file, lock):
    logging.debug("Fetched data at " +
                  str(dt.datetime.now().strftime("%H:%M:%S")) + "!")
    resp: requests.Response = requests.get(url)
    respObj = json.loads(resp.content)
    lock.acquire()
    pickle.dump(respObj, open(file, "w+b"))
    lock.release()

def start_up(url, file, lock):
    global run_loading_screen
    run_loading_screen = True
    loading_screen_thread = threading.Thread(target=loading_screen)
    loading_screen_thread.start()
    fetch_data_with_repeat(url, file, lock)
    run_loading_screen = False
    time.sleep(0.3)

def loading_screen():
    block_orientation = -90
    rotate = 0
    inreverse = False
    width = 64
    height = 16
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, block_orientation=block_orientation,
                            rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse,
                            width=width, height=height)
    device.contrast(0x10)

    x = 0
    global run_loading_screen
    while (run_loading_screen):
        with canvas(device) as draw:
            loading_screen_width = 39
            draw.point(get_image_as_list(
                "icons/loading.txt", x, 8), fill="white")
            draw.point(get_image_as_list(
                "icons/loading.txt", x+loading_screen_width, 8), fill="white")
            draw.point(get_image_as_list(
                "icons/loading.txt", x+(loading_screen_width*2), 8), fill="white")
            x -= 1
            if x == -loading_screen_width:
                x = 0
            #self.display_minutes(draw, s8_herrsching_minutes, self.s8_herrsching_minutes_cache, 9, 0)
            text(draw, (0, 0), "Dagl-Info", fill="white", font=proportional(LCD_FONT))
    #device.cleanup()
    print("Loaded!")

def fetch_data_with_repeat(url, file, lock):
    resp = None
    while True:
        logging.debug("Fetched data at " +
                    str(dt.datetime.now().strftime("%H:%M:%S")) + "!")       
        resp: requests.Response = requests.get(url)
        if resp.content == None or len(resp.content) == 0:
            time.sleep(10)
        else:
            break
    respObj = json.loads(resp.content)
    lock.acquire()
    pickle.dump(respObj, open(file, "w+b"))
    lock.release()

def start_data_fetch_thread(mvg_api, api_file, lock):
    data_fetcher = threading.Thread(
                target=fetch_data, args=(mvg_api, api_file, lock))
    data_fetcher.start()

def load_data(api_file, lock):
    lock.acquire()
    respObj = pickle.load(open(api_file, "rb"))
    lock.release()
    return respObj

def get_minutes(search_for, amount, api_data):
    min_list = list()
    for departure in api_data["departures"]:
        abfahrt_dict = dict()
        if amount == 0:
            break
        for current_search in search_for:
            if departure["destination"].find(current_search) != -1:
                destination = departure["destination"]
                abfahrt_dict["destination"] = departure["destination"]
                cancelled = departure["cancelled"]
                delayKey = "delay"
                live = True
                if delayKey in departure.keys():
                    delay = departure["delay"]
                else:
                    delay = 0
                    live = False
                sev: bool = departure["sev"]
                if not cancelled:
                    abfahrt_dict["time"] = dt.datetime.fromtimestamp(departure["departureTime"]/1000)
                    seconds = floor((dt.datetime.fromtimestamp(floor(
                        departure["departureTime"]/1000)) - dt.datetime.now()).total_seconds()) + (delay * 60)
                    if seconds > 0:
                        minutes = floor(seconds / 60)
                        secondsUnderSixty: str = seconds
                        while seconds >= 60:
                            seconds -= 60
                            secondsUnderSixty = seconds
                    else:
                        minutes = 0
                        departureTimeDisplay = "Jetzt"
                    abfahrt_dict["minutes"] = minutes
                    min_list.append(abfahrt_dict)
                    if sev:
                        destination += " SEV"
                else:
                    departureTimeDisplay = "X"
                if live:
                    delay = str(delay) + "m"
                else:
                    delay = "Not Live"
                amount -= 1
    return min_list
        

def process_data(api_data):
    destination = api_data["destination"]
    cancelled = api_data["cancelled"]
    delayKey = "delay"
    live = True
    if delayKey in api_data.keys():
        delay = api_data["delay"]
    else:
        delay = 0
        live = False
    sev: bool = api_data["sev"]
    if not cancelled:
        seconds = floor((dt.datetime.fromtimestamp(floor(
            api_data["departureTime"]/1000)) - dt.datetime.now()).total_seconds()) + (delay * 60)
        if seconds > 0:
            minutes = floor(seconds / 60)
            secondsUnderSixty: str = seconds
            while seconds >= 60:
                seconds -= 60
                secondsUnderSixty = seconds
            departureTimeDisplay: str = str(
                minutes) + "m " + str(secondsUnderSixty) + "s"
        else:
            departureTimeDisplay = "Jetzt"
        if sev:
            destination += " SEV"
    else:
        departureTimeDisplay = "X"
    if live:
        delay = str(delay) + "m"
    else:
        delay = "Not Live"
    return destination, departureTimeDisplay, delay

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    display = DisplayDriver()
    mvg_api = "https://www.mvg.de/api/fahrinfo/departure/de:09162:700"
    create_folder(data_folder)
    api_file = os.path.join(data_folder, "departures.p")
    lock = threading.Lock()
    content = list()
    start_up(mvg_api, api_file, lock)
    #first_fetch_data(mvg_api, api_file, lock, display)
    respObj = pickle.load(open(api_file, "rb"))
    i = 0
    refresh_counter = 0
    while True:
        if refresh_counter == 4:
            tempRespObj = load_data(api_file, lock)
            if "departures" in tempRespObj.keys() and len(tempRespObj["departures"]) > 0:
                respObj = tempRespObj
        if refresh_counter >= 45:
            start_data_fetch_thread(mvg_api, api_file, lock)
            refresh_counter = 0
        refresh_counter += 1
        min_list_flughafen_s_bahn = get_minutes(s8_to_airport, 3, respObj)
        min_list_city_s_bahn = get_minutes(s8_into_city, 3, respObj)
        for api_data in respObj["departures"]:
            destination, departure_time_display, delay = process_data(api_data)
            content.append([destination, departure_time_display, delay])
            i += 1
            if i > show_next_connections:
                break
        i = 0

        header = ["Richtung", "Minuten", "Verspätung"]
        print(tabulate(content, headers=header))
        print("")
        display.s_bahn_layout(min_list_flughafen_s_bahn, min_list_city_s_bahn)
 
        content = list()
        time.sleep(1)

if __name__ == "__main__":
    main()