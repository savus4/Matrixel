from screens.screen import screen
from screens.helper import calc_string_length

from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

class scrolling_text(screen):

    def __init__(self, base_priority, elevated_priority, animatable=False, animation_state=0, animation_delay=60, first_line_font=LCD_FONT , second_line_font=LCD_FONT):
        super().__init__(base_priority, elevated_priority, animatable, animation_state)
        self.first_line = str()
        self.second_line = str()
        self.animation_delay = animation_delay
        self.first_line_font = first_line_font
        self.second_line_font = second_line_font
        self.text_changed = False

    def set_first_line(self, text):
        if text != self.first_line:
            self.first_line = text
            self.text_changed = True

    def set_second_line(self, text):
        if text != self.second_line:
            self.second_line = text
            self.text_changed = True

    def display(self, screen_changed):
        super().display(screen_changed)

        first_line_length = calc_string_length(self.first_line)
        second_line_length = calc_string_length(self.second_line)
        if second_line_length > first_line_length:
            display_string_length = second_line_length
        else:
            display_string_length = first_line_length

        self.animation_state = rolling_frame_counter
        animation_end_buffer = 7
        animation_frames_duration = self.animation_delay + animation_end_buffer + display_string_length
        if self.text_changed:
            print("text_changed")
            self.animation_state = 0
        else:
            self.animation_state = rolling_frame_counter % animation_frames_duration

        text_begin = 0
        #print("frame counter: " + str(self.animation_state) + ", width: " + str(self.device.width) + " display str length: " + str(display_string_length))

        if display_string_length > self.device.width:
            #print("anim must")
            if self.animation_state > self.animation_delay:
                #print("animation state in if: " + str(self.animation_state))
                text_begin = self.animation_delay - self.animation_state
            if text_begin < (-display_string_length - animation_end_buffer):
                #print("reset animation!")
                self.animation_state = 0
        if (display_string_length > self.device.width) or self.text_changed:
            upper_shift = text_begin if first_line_length > self.device.width else 0
            lower_shift = text_begin if second_line_length > self.device.width else 0
            with canvas(self.device) as draw:
                text(draw, (upper_shift, 0), self.first_line,
                        fill="white", font=proportional(self.first_line_font))
                text(draw, (lower_shift, 9), self.second_line,
                    fill="white", font=proportional(self.second_line_font))
            self.text_changed = False