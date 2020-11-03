import threading
from scraper import Scraper
import time
from display import DisplayDriver

def got_new_data():
    print("Last refresh: " + str(scraper.last_refresh))
    display.s_bahn_layout(scraper.s8_airport_min_list, scraper.s8_city_min_list, "")

# Init display
display = DisplayDriver()

# Get data
poll_time = 30 #seconds
scraper = Scraper()
threading.Thread(target=scraper.get_data, args=[poll_time, got_new_data]).start()


