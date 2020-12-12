from datetime import datetime
from pprint import pprint

class Messages_Manager():
    def __init__(self):
        self.messages = list()

    def new_message(self, message):
        self.messages.append(message)
        print("ALL MESSAGES:")
        for msg in self.messages:
            pprint(str(msg))

    def get_last_message(self):
        return self.messages[-1]
    
    def get_last_message_from(self, username):
        for message in reversed(self.messages):
            if username == message.username:
                return message

    def has_new_message(self):
        for message in self.messages:
            if message.unread:
                return True
        return False

    def get_newest_message(self):
        for message in self.messages:
            if message.unread:
                return message

    def mark_oldest_unread_message_as_read(self):
        for message in self.messages:
            if message.unread:
                message.unread = False
                return


class DisplayMessage():

    def __init__(self, username, message):
        print("Creating new Message")
        self.message = message
        self.username = username
        self.creation_timestamp = datetime.now()
        self.unread = True


    def __str__(self) -> str:
        return "From: " + self.username + ": " + self.message
