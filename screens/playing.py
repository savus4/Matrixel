from screens.scrolling_text import scrolling_text

class playing(scrolling_text):

    def __init__(self, sonos_state, base_priority=100, elevated_priority=10):
        super().__init__(base_priority, elevated_priority, animatable=True)
        self.sonos_state = sonos_state

    def display(self, rolling_frame_counter, last_frame):
        #self.state = display_state.playing
        if self.priority != self.elevated_priority:
            self.set_first_line("No Active")
            self.set_second_line("Player.")
        super().display(rolling_frame_counter, last_frame)

    def refresh_priority(self):
        playing_rooms = self.sonos_state.get_playing_rooms()
        #self.state = display_state.playing
        if playing_rooms:
            self.set_first_line(list(playing_rooms.values())[0].current_track.name)
            self.set_second_line(list(playing_rooms.values())[0].current_track.artist)
            self.priority = self.elevated_priority
        else:
            self.priority = self.base_priority