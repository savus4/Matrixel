from screens.scrolling_text import scrolling_text
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

class messages(scrolling_text):

    def __init__(self, msg_manager, base_priority=90, elevated_priority=4):
        super().__init__(base_priority, elevated_priority, animation_delay=30, first_line_font=CP437_FONT)
        self.msg_manager = msg_manager
        self.cur_msg_cache = None

    def display(self, rolling_frame_counter, last_frame):
        msg_length = self.cur_msg_cache.length
        text_begin = 0
        if self.priority == self.elevated_priority:
            self.first_line = self.cur_msg_cache.username
            self.second_line = self.cur_msg_cache.message
        else:
            self.first_line = "Oh no..."
            self.second_line = "a bug! :("
        super().display(rolling_frame_counter, last_frame)

    
    def refresh_priority(self):
        possibly_new_message = self.msg_manager.get_newest_message()
        #print(str(possibly_new_message)+ "has new message: " + str(self.msg_manager.has_new_message()))

        if self.msg_manager.has_new_message():
            print("new message!!")
            self.new_message = False
            if id(possibly_new_message) != id(self.cur_msg_cache):
                self.cur_msg_cache = possibly_new_message
                print("new message")
                self.new_message = True
            self.priority = self.elevated_priority
            #return True
        else:
            #if self.cur_msg_cache:
             #   self.wake_up()
            self.cur_msg_cache = None
            self.priority = self.base_priority
            return False