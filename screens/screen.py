from luma.core.render import canvas

class screen():

    def __init__(self, base_priority, elevated_priority, animatable=False, animation_state=0):
        self.animatable = animatable
        self.animation_state = animation_state
        self.base_priority = base_priority
        self.elevated_priority = elevated_priority
        self.priority = base_priority

    def add_device(self, device):
        self.device = device

    def refresh_priority(self):
        pass

    def display(self, rolling_frame_counter, last_frame):
        if self.animatable:
            if type(last_frame) is not self:
                self.animation_state = 0
            else:
                self.animation_state += 1
        