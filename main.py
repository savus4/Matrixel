import threading
from scraper import Scraper
import time
from display import DisplayDriver


def main():
    # Init display
    display = DisplayDriver()

    # Get data
    poll_time = 30 #seconds
    scraper = Scraper()
    threading.Thread(target=scraper.get_data, args=[display.s_bahn_layout]).start()

    while(True):
        display.s_bahn_layout(scraper, "")
        time.sleep(0.1)


if __name__ == "__main__":
    main()