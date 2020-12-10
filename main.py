import threading
from scraper import Scraper
import time
from display import DisplayDriver
import server
from dagl_msg import Dagl_Message

def main():
    # Init display
    display = DisplayDriver()

    # Get data
    poll_time = 30 #seconds
    scraper = Scraper()
    threading.Thread(target=scraper.get_data, args=[display.s_bahn_layout]).start()

    # Local server for short messages
    msg = Dagl_Message()
    msg.message = "test"
    display_sleeping = False
    threading.Thread(target=server.run, args=[msg, display_sleeping]).start()


    message = None
    while(True):
        #print("sleeping: " + str(display_sleeping))
        display.s_bahn_layout(scraper, message)
        time.sleep(0.1)


if __name__ == "__main__":
    main()