from screens.screen import screen

class black(screen):

    def __init__(self, base_priority=50, elevated_priority=5, animatable=False, animation_state=0):
        super().__init__(base_priority, elevated_priority)

    def refresh_priority(self):
        pass

    def display(self, rolling_frame_counter, last_frame):
        super().display(rolling_frame_counter, last_frame)
        if type(last_frame) is not self:
            self.device.clear()