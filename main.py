import threading
from scraper import Scraper
import time
from display import DisplayDriver
#import server
from Messages_Manager import Messages_Manager
from departures import Departures
from line_manager import Line_Manager
from sonos_state import Sonos_State
from stations import s8
import flask_server
from luma.core.sprite_system import framerate_regulator


def main():
    msg_manager = Messages_Manager()

    s8_city = Departures(s8.name, s8.into_city, s8.into_city_warning, s8.into_city_times)
    s8_airport = Departures(s8.name, s8.to_airport, s8.to_airport_warning, s8.to_airport_times)
    lines = Line_Manager([s8_city, s8_airport])

    sonos_state = Sonos_State("http://localhost:5005", ["Beam", "Küche", "Esszimmer"])
    
    # Init display
    display = DisplayDriver(msg_manager, lines, sonos_state, startup_screen=True)

    # Get data
    #poll_time = 30 #seconds
    scraper = Scraper(lines)
    threading.Thread(target=scraper.get_data).start()

    # Local server for short messages
    #threading.Thread(target=server.run, args=[msg, display_sleeping]).start()
    threading.Thread(target=flask_server.start_server, args=[display.toggle_sleep_mode, msg_manager]).start()

    curr_time = time.time()
    regulator = framerate_regulator(fps=20)
    while(True):
        with regulator:
            #print("sleeping: " + str(display_sleeping))
            display.main_layout()
            
            #time.sleep(0.05)


if __name__ == "__main__":
    main()