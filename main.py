import threading
from scraper import Scraper
import time
from display import DisplayDriver
#import server
from Messages_Manager import Messages_Manager
import flask_server

def main():
    msg_manager = Messages_Manager()
    # Init display
    display = DisplayDriver(msg_manager)

    # Get data
    poll_time = 30 #seconds
    scraper = Scraper()
    threading.Thread(target=scraper.get_data).start()

    # Local server for short messages
    #threading.Thread(target=server.run, args=[msg, display_sleeping]).start()
    threading.Thread(target=flask_server.start_server, args=[display.toggle_sleep_mode, msg_manager]).start()


    message = None
    while(True):
        #print("sleeping: " + str(display_sleeping))
        display.main_layout(scraper, message)
        time.sleep(0.1)


if __name__ == "__main__":
    main()