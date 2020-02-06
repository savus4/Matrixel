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
from helper import make_string_from_list


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

def first_fetch_data(url, file, lock):
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
    mvg_api = "https://www.mvg.de/api/fahrinfo/departure/de:09162:700"
    create_folder(data_folder)
    api_file = os.path.join(data_folder, "departures.p")
    lock = threading.Lock()
    content = list()
    first_fetch_data(mvg_api, api_file, lock)
    respObj = pickle.load(open(api_file, "rb"))
    display = DisplayDriver()
    i = 0
    refresh_counter = 0
    while True:
        if refresh_counter == 4:
            respObj = load_data(api_file, lock)
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