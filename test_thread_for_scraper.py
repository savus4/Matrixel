import threading
from scraper import Scraper
import time

poll_time = 30 #seconds
scraper = Scraper()
threading.Thread(target=scraper.get_data, args=[poll_time]).start()

for i in range(0,120):
    print("last refresh: " + str(scraper.last_refresh) + ", " + str(i))
    time.sleep(0.5)


