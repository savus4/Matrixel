from datetime import datetime

class Messages_Manager():
    def __init__(self, message_added_callback):
        self.messages = list()
        self.message_added_callback = message_added_callback

    def new_message(self, message):
        self.messages.append(message)
        self.message_added_callback(self)

    def get_last_message(self):
        return self.messages[-1]
    
    def get_last_message_from(self, username):
        for message in reversed(self.messages):
            if username == message.username:
                return message

class DisplayMessage():

    def __init__(self, username, message):
        self.message = message
        self.username = username
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        return self.message
