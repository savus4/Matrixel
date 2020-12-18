import time
import datetime as dt
from datetime import time as dtTime
from math import floor
import json
import os
from typing import List
from pprint import pprint

class Departure:

    def __init__(self, departure, times, interval) -> None:
        self.__times = times
        self.__interval = interval
        self.parse_departure_dict(departure)
        
    def parse_departure_dict(self, departure):
        self.destination = departure["destination"]
        self.cancelled = departure["cancelled"]
        self.live = True
        if "delay" in departure.keys():
            self.delay = departure["delay"]
        else:
            self.delay = 0
            self.live = False
        self.sev: bool = departure["sev"]
        if not self.cancelled:
            self.current_departure_time = dt.datetime.fromtimestamp(departure["departureTime"]/1000) + dt.timedelta(minutes = self.delay)
            self.as_usual = self.generate_as_usual(self.current_departure_time)
        else:
            self.as_usual = False

    def seconds(self) -> int:
        now = dt.datetime.now()
        seconds = floor((self.current_departure_time - now).total_seconds()) + (self.delay * 60)
        return seconds if seconds > 0 else 0

    def minutes(self):
        return floor(self.seconds() / 60)

    def generate_as_usual(self, time):
        as_usual = False
        next_possible_departures = self.get_next_exptected_times()
        for next_possible_departure in next_possible_departures:
            #print(str(time) + " Possible: " + str(next_possible_departure) + "; Difference: " + str((next_possible_departure - time).total_seconds()))
            if (time - next_possible_departure).total_seconds() <= 100 and (time - next_possible_departure).total_seconds() >= -50:
                as_usual = True
            #print(str(time) + " Possible: " + str(next_possible_departure) + "; Difference: " + str((time - next_possible_departure).total_seconds()))

        return as_usual

    def get_next_exptected_times(self, number_next_exptected_times=3):
        now = dt.datetime.now()
        next_possible_departures = list()
        #print("Now: " + str(now))
        # if now.hour == 23:
        #     add_delta = -23
        #     today = dt.date(now.year, now.month, now.day+1)
        # else:
        #     add_delta = 1
        #     today = dt.date.today()

        #cur_hour = now.hour
        cur_departure = dt.datetime.combine(dt.date(now.year, now.month, now.day), dt.time(now.hour, self.__times[0]))
        while len(next_possible_departures) < number_next_exptected_times:
            if cur_departure > now:
                next_possible_departures.append(cur_departure)
            cur_departure += dt.timedelta(minutes=self.__interval)



        # next_possible_departures = list()
        # for normal_departure_minute in self.times:
        #     next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour, normal_departure_minute)))

        # for normal_departure_minute in self.times:
        #     next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour + add_delta, normal_departure_minute)))

    
        # if (now.minute > 49 and now.minute <= 59) or (now.minute >= 0 and now.minute <= 9):
        #     next_possible_departures = next_possible_departures[3:]
        #     #next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour+1, 9)))
        # if now.minute >= 0 and now.minute <= 9:
        #     pass
        #     #next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour, 9)))
        # if now.minute > 9 and now.minute <= 29:
        #     next_possible_departures = next_possible_departures[1:4]

        #     #next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour, 29)))
        # if now.minute > 29 and now.minute <= 49:
        #     next_possible_departures = next_possible_departures[2:5]
        

        # for cur_end_station in self.s8_into_city_stations:
        #     if direction.find(cur_end_station) != -1:
        #         next_possible_departures = [dt.datetime.combine(today, dt.time(now.hour, 9)), dt.datetime.combine(today, dt.time(now.hour, 29)), dt.datetime.combine(today, dt.time(now.hour, 49)),
        #                                     dt.datetime.combine(today, dt.time(now.hour+add_delta, 9)), dt.datetime.combine(today, dt.time(now.hour+add_delta, 29)), dt.datetime.combine(today, dt.time(now.hour+add_delta, 49))]

        #         if (now.minute > 49 and now.minute <= 59) or (now.minute >= 0 and now.minute <= 9):
        #             next_possible_departures = next_possible_departures[3:]
        #             #next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour+1, 9)))
        #         if now.minute >= 0 and now.minute <= 9:
        #             pass
        #             #next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour, 9)))
        #         if now.minute > 9 and now.minute <= 29:
        #             next_possible_departures = next_possible_departures[1:4]

        #             #next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour, 29)))
        #         if now.minute > 29 and now.minute <= 49:
        #             next_possible_departures = next_possible_departures[2:5]

        #             #next_possible_departures.append(dt.datetime.combine(today, dt.time(now.hour, 49)))
                    

        #         #print("dir: " + direction + " cur end station: " + cur_end_station)
        # for cur_end_station in self.s8_to_airport_stations:
        #     if direction.find(cur_end_station) != -1:
        #         #print("dir: " + direction + " cur end station: " + cur_end_station)
        #         next_possible_departures = [dt.datetime.combine(today, dt.time(now.hour, 11)), dt.datetime.combine(today, dt.time(now.hour, 31)), dt.datetime.combine(today, dt.time(now.hour, 51)),
        #                                     dt.datetime.combine(today, dt.time(now.hour+add_delta, 11)), dt.datetime.combine(today, dt.time(now.hour+add_delta, 31)), dt.datetime.combine(today, dt.time(now.hour+add_delta, 51))]
    
        #         if (now.minute > 51 and now.minute <= 59) or (now.minute >= 0 and now.minute <= 11):
        #             next_possible_departures = next_possible_departures[3:]

        #         if now.minute > 11 and now.minute <= 31:
        #             next_possible_departures = next_possible_departures[1:4]

        #         if now.minute > 31 and now.minute <= 51:
        #             next_possible_departures = next_possible_departures[2:5]
        #print(str(next_possible_departures))
        return next_possible_departures

class Departures:

    def __init__(self, name, stations, warning_stations, times, official_direction=None) -> None:
        self.name = name
        self.stations = stations
        self.warning_stations = warning_stations
        self.times = times
        self.interval = self.calc_interval(times)
        if official_direction:
            self.direction = official_direction
        else:
            self.direction = stations[0]
        self.last_refresh = None
        self.minutes_since_last_refresh = None
        self.min_list = None
        self.departures: List[Departure] = list()

    def new_data(self, response):
        self.add_departures(response)

    def add_departures(self, response):
        new_departures = list()
        #pprint("New Response *********************")
        #pprint(response)
        for departure in response["departures"]:
            if departure["destination"] in self.stations:
                new_departures.append(Departure(departure, self.times, self.interval))
            #for current_search in self.stations:
            #    if departure["destination"].find(current_search) != -1:
            #        self.departures.append(Departure(departure, self.times, self.interval))
        if len(new_departures) > 0:
            self.departures = new_departures
            self.last_refresh = dt.datetime.now()
            self.minutes_since_last_refresh = dt.datetime.now() - self.last_refresh

    def calc_interval(self, times):
        intervals = list()
        for i in range(len(times)):
            if i + 1 < len(times):
                intervals.append(times[i+1]-times[i])
            else:
                intervals.append(60 - times[-1] + times[0])
        if len(set(intervals)) == 1:
            return intervals[0]
        else:
            raise Exception("Different intervals between departures: " + str(intervals) + os.linesep + "Not implemented yet.")

    def get_next_connections_excerpt(self, number_next_connections) -> list:
        if len(self.departures) >= number_next_connections:
            return self.departures[0:number_next_connections]
        else:
            return self.departures

    def check_as_usual(self, number_departures=3):
        i = 0  
        for departure in self.departures:
            if i < number_departures:
                if not departure.as_usual:
                    return False
            else:
                return True
            i += 1
