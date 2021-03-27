import threading
from scraper import Scraper
import time

from display import DisplayDriver
from screens.playing import playing
from screens.black import black
from screens.messages import messages

from Messages_Manager import Messages_Manager
from departures import Departures
from line_manager import Line_Manager
from sonos_state import Sonos_State
from stations import s8
import flask_server
from luma.core.sprite_system import framerate_regulator


def main():

    s8_city = Departures(s8.name, s8.into_city, s8.into_city_warning, s8.into_city_times)
    s8_airport = Departures(s8.name, s8.to_airport, s8.to_airport_warning, s8.to_airport_times)
    lines = Line_Manager([s8_city, s8_airport])

    # Create black / idle screen
    black_screen = black()

    # Setup Sonos playing screen
    #sonos_state = Sonos_State("http://192.168.178.21:5005", ["Beam", "Küche", "Esszimmer"])
    sonos_state = Sonos_State("http://localhost:5005", ["Beam", "Küche", "Esszimmer"])
    playing_screen = playing(sonos_state)

    # Setup messages screen
    msg_manager = Messages_Manager()
    messages_screen = messages(msg_manager)
    
    # Init display
    display = DisplayDriver(startup_screen=True)
    display.add_screen(playing_screen)
    display.add_screen(black_screen)
    display.add_screen(messages_screen)

    # Get departure data
    #poll_time = 30 #seconds
    #scraper = Scraper(lines)
    #threading.Thread(target=scraper.get_data).start()

    # Local server for short messages
    #threading.Thread(target=server.run, args=[msg, display_sleeping]).start()
    threading.Thread(target=flask_server.start_server, args=[display.toggle_sleep_mode, msg_manager]).start()

    curr_time = time.time()
    regulator = framerate_regulator(fps=6)
    while True:
        with regulator:
            #print("sleeping: " + str(display_sleeping))
            display.new_main()


if __name__ == "__main__":
    main()