from enum import Enum, auto

class display_state(Enum):
    black = auto()
    idle = auto()
    sleeping = auto()
    playing = auto()
    departures = auto()
    messages = auto()
    startup_screen = auto()