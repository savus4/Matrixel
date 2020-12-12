from datetime import datetime

class Messages_Manager():
    def __init__(self):
        self.messages = list()

    def new_message(self, message):
        self.messages.append(message)

    def get_last_message(self):
        return self.messages[-1]
    
    def get_last_message_from(self, username):
        for message in reversed(self.messages):
            if username == message.username:
                return message

    def has_current_message(self):
        return False

class DisplayMessage():

    def __init__(self, username, message):
        self.message = message
        self.username = username
        self.creation_timestamp = datetime.now()


    def __str__(self) -> str:
        return self.message
