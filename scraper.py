#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import logging
import requests
import time
import datetime as dt
from datetime import time as dtTime
import json
from math import floor
import pprint


class Scraper:

    data_folder = "/home/pi/Documents/mvg_departure_monitor/data/"
    s8_into_city_stations = ["Herrsching", "Weßling", "Gilching-Argelsried", "Pasing", "Ostbahnhof", "Leuchtenbergring"]
    s8_into_city_warning = ["Ostbahnhof", "Leuchtenbergring", "Rosenheimer", "Isartor"]
    s8_to_airport_stations = ["Flughafen", "Ismaning", "Unterföhring", "Johanneskirchen"]
    s8_to_airport_warning = ["Unterföhring"]
    
    daglfing_sbahn_api = "https://www.mvg.de/api/fahrinfo/departure/de:09162:700"

    s8_city_min_list = list()
    s8_airport_min_list = list()

    last_refresh = None
    minutes_since_last_refresh = None

    raw_api_data = dict()

    def get_data(self, refresh_s_bahn_layout=None):
        while True:
            self.fetch_data()
            self.s8_city_min_list = self.get_minutes(self.s8_into_city_stations)
            self.s8_airport_min_list = self.get_minutes(self.s8_to_airport_stations)
            if refresh_s_bahn_layout:
                refresh_s_bahn_layout(self)
            #print(str(self.s8_city_min_list))
            time.sleep(self.get_adaptive_period())
        

    def fetch_data(self):
        resp = None
        while True: 
            try:
                resp: requests.Response = requests.get(self.daglfing_sbahn_api)
                if resp == None or resp.content == None or len(resp.content) == 0:
                    print("Failed to fetch at " + str(dt.datetime.now()))
                    self.minutes_since_last_refresh = dt.datetime.now() - self.last_refresh
                    time.sleep(10)
                else:
                    break
            except requests.exceptions.RequestException as e:
                print("Failed to fetch at " + str(dt.datetime.now()) + "\n" + 
                      "Reason: " + str(e))
                self.minutes_since_last_refresh = dt.datetime.now() - self.last_refresh
                time.sleep(10)
        logging.debug("Fetched data at " +
                        str(dt.datetime.now().strftime("%H:%M:%S")) + "!")    
        self.raw_api_data = json.loads(resp.content)
        self.last_refresh = dt.datetime.now()
        self.minutes_since_last_refresh = dt.datetime.now() - self.last_refresh

    def get_minutes(self, search_for):
        min_list = list()
        now = dt.datetime.now()
        for departure in self.raw_api_data["departures"]:
            abfahrt_dict = dict()
            for current_search in search_for:
                if departure["destination"].find(current_search) != -1:
                    destination = departure["destination"]
                    abfahrt_dict["destination"] = departure["destination"]
                    cancelled = departure["cancelled"]
                    delayKey = "delay"
                    live = True
                    if delayKey in departure.keys():
                        delay = departure["delay"]
                        abfahrt_dict["delay"] = departure["delay"]
                    else:
                        delay = 0
                        live = False
                    sev: bool = departure["sev"]
                    if not cancelled:
                        abfahrt_dict["time"] = dt.datetime.fromtimestamp(departure["departureTime"]/1000) + dt.timedelta(minutes = delay)
                        abfahrt_dict["as_usual"] = self.check_as_usual(abfahrt_dict["time"], abfahrt_dict["destination"])
                        seconds = floor((dt.datetime.fromtimestamp(floor(
                            departure["departureTime"]/1000)) - now).total_seconds()) + (delay * 60)
                        if seconds > 0:
                            minutes = floor(seconds / 60)
                        else:
                            minutes = 0
                            departureTimeDisplay = "Jetzt"
                        abfahrt_dict["minutes"] = minutes
                        min_list.append(abfahrt_dict)
                        if sev:
                            destination += " SEV"
                    else:
                        abfahrt_dict["time"] = "X"
                        abfahrt_dict["minutes"] = "X"
                        abfahrt_dict["as_usual"] = False
                        min_list.append(abfahrt_dict)
                        departureTimeDisplay = "X"
                    if live:
                        delay = str(delay) + "m"
                    else:
                        delay = "Not Live"
        return min_list

    def check_as_usual(self, time, direction):
        as_usual = False
        next_possible_departures = self.get_next_exptected_s8_times(direction)
        for next_possible_departure in next_possible_departures:
            #print(str(time) + " Possible: " + str(next_possible_departure) + "; Difference: " + str((next_possible_departure - time).total_seconds()))
            if (time - next_possible_departure).total_seconds() <= 100 and (time - next_possible_departure).total_seconds() >= 0:
                as_usual = True
            #print(str(time) + " Possible: " + str(next_possible_departure) + "; Difference: " + str((time - next_possible_departure).total_seconds()))

        return as_usual

    def get_next_exptected_s8_times(self, direction):
        now = dt.datetime.now()
        next_possible_departures = list()
        #print("Now: " + str(now))
        if now.hour == 23:
            add_delta = -23
            today = dt.date(now.year, now.month, now.day+1)
        else:
            add_delta = 1
            today = dt.date.today()
        for cur_end_station in self.s8_into_city_stations:
            if direction.find(cur_end_station) != -1:
                next_possible_departures = [dt.datetime.combine(today, dt.time(now.hour, 9)), dt.datetime.combine(today, dt.time(now.hour, 29)), dt.datetime.combine(today, dt.time(now.hour, 49)),
                                            dt.datetime.combine(today, dt.time(now.hour+add_delta, 9)), dt.datetime.combine(today, dt.time(now.hour+add_delta, 29)), dt.datetime.combine(today, dt.time(now.hour+add_delta, 49))]
    
                if (now.minute > 49 and now.minute <= 59) or (now.minute >= 0 and now.minute <= 9):
                    next_possible_departures = next_possible_departures[3:]
                    #next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour+1, 9)))
                if now.minute >= 0 and now.minute <= 9:
                    pass
                    #next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour, 9)))
                if now.minute > 9 and now.minute <= 29:
                    next_possible_departures = next_possible_departures[1:4]

                    #next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour, 29)))
                if now.minute > 29 and now.minute <= 49:
                    next_possible_departures = next_possible_departures[2:5]

                    #next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour, 49)))
                    

                #print("dir: " + direction + " cur end station: " + cur_end_station)
        for cur_end_station in self.s8_to_airport_stations:
            if direction.find(cur_end_station) != -1:
                #print("dir: " + direction + " cur end station: " + cur_end_station)
                next_possible_departures = [dt.datetime.combine(today, dt.time(now.hour, 11)), dt.datetime.combine(today, dt.time(now.hour, 31)), dt.datetime.combine(today, dt.time(now.hour, 51)),
                                            dt.datetime.combine(today, dt.time(now.hour+add_delta, 11)), dt.datetime.combine(today, dt.time(now.hour+add_delta, 31)), dt.datetime.combine(today, dt.time(now.hour+add_delta, 51))]
    
                if (now.minute > 51 and now.minute <= 59) or (now.minute >= 0 and now.minute <= 11):
                    next_possible_departures = next_possible_departures[3:]

                if now.minute > 11 and now.minute <= 31:
                    next_possible_departures = next_possible_departures[1:4]

                if now.minute > 31 and now.minute <= 51:
                    next_possible_departures = next_possible_departures[2:5]
        #print(str(next_possible_departures))
        return next_possible_departures

    def get_adaptive_period(self):
        now_time = dt.datetime.utcnow().time()
        if now_time >= dtTime(2, 30) and now_time <= dtTime(5, 10):
            return 57
        else:
            return 29

#print("test")
#scraper = Scraper()
#scraper.get_data()
#pprint.pprint(str(scraper.s8_airport_min_list))