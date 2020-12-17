from datetime import datetime
from departures import Departures
from typing import List

class Line_Manager():

    def __init__(self, lines: List[Departures]) -> None:
        self.lines = lines

    def new_data(self, data):
        for line in self.lines:
            line.new_data(data)

    def check_as_usual(self, number_of_departures=3) -> bool:
        as_usual = True
        for line in self.lines:
            if not line.check_as_usual(number_of_departures):
                as_usual = False
        return as_usual

    def last_refresh(self) -> datetime:
        current_last_refresh = datetime.now()
        for line in self.lines:
            if line.last_refresh < current_last_refresh:
                current_last_refresh = line.last_refresh
        return current_last_refresh
