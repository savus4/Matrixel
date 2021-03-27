import requests
import threading
from typing import List, Dict
from pprint import pprint
import datetime as dt
import time
import json
import os
from pathlib import Path
from enum import Enum, auto
import logging

class Sonos_State():

    def __init__(self, server_url, room_names):
        self.rooms: Dict[str, Sonos_Room] = dict()
        self.create_rooms(room_names)
        threading.Thread(target=self.sonos_state_fetcher, args=[server_url]).start()

    def create_rooms(self, room_names):
        for room_name in room_names:
            self.rooms[room_name] = Sonos_Room(room_name)

    def room_is_playing(self, room_name: str):
        return self.rooms[room_name].playing_state == playing_state.playing and self.rooms[room_name].playing_type == "track"

    def any_room_is_playing(self):
        for room in self.rooms.values():
            if self.room_is_playing(room.name):
                return True
        return False

    def get_playing_rooms(self) -> dict:
        playing_rooms = dict()
        for room in self.rooms.values():
            if room.playing_state == playing_state.playing:
                playing_rooms[room.name] = room
        return playing_rooms

    def sonos_state_fetcher(self, url) -> str:
            while True:
                for room in self.rooms.values():
                    while True:
                        try:
                            resp: requests.Response = requests.get(url + "/" + room.name + "/state", timeout=3.0)
                            if resp == None or resp.content == None or len(resp.content) == 0:
                                print("Failed to fetch at " + str(dt.datetime.now()))
                                self.minutes_since_last_refresh = dt.datetime.now() - self.last_refresh
                                time.sleep(2)
                            else:
                                break
                        except requests.exceptions.RequestException as e:
                            print("Failed to fetch at " + str(dt.datetime.now()) + "\n" + 
                                    "Reason: " + str(e))
                            time.sleep(2)
                    #pprint(resp.content)
                    room.process_new_state(json.loads(resp.content))
                time.sleep(1)

    def __str__(self):
        playing_rooms = self.get_playing_rooms()
        if playing_rooms:
            return list(playing_rooms.values())[0].current_track.name + os.linesep + list(playing_rooms.values())[0].current_track.artist
        else:
            return "No room is playing."

class playing_state(Enum):
    playing = auto()
    paused = auto()

class Sonos_Room():

    def __init__(self, name: str):
        self.name: str = name
        self.playing_state = playing_state.paused
        self.mute = False
    
    
    def process_new_state(self, state_object: json):
        #pprint(state_object)
        self.playing_state = self.parse_playing_state(state_object["playbackState"])
        self.playing_type = state_object["currentTrack"]["type"]
        self.current_track = Track(state_object["currentTrack"])
        self.mute = state_object["mute"]
        self.elapsed_time = state_object["elapsedTime"]
        self.next_track = Track(state_object)

    def parse_playing_state(self, playing_state_str):
        if playing_state_str == "PLAYING":
            return playing_state.playing
        elif playing_state_str in ["PAUSED_PLAYBACK", "STOPPED", "TRANSITIONING"]:
            return playing_state.paused
        else:
            logging.error("Unknown playing state: " + playing_state_str + os.linesep + "State set to paused.")
            return playing_state.paused


class Track():

    def __init__(self, current_track_object: json):
        self.name = ""
        self.artist = ""
        self.duration = ""
        self.album = ""
        if "title" in current_track_object.keys():
            self.name = current_track_object["title"]
            self.artist = current_track_object["artist"]
            self.duration = current_track_object["duration"]
            self.album = current_track_object["album"]

if __name__ == "__main__":
    state = Sonos_State("http://192.168.178.51:5005", ["Beam", "Küche", "Esszimmer"])
    while True:
        print(str(state))
        time.sleep(1)