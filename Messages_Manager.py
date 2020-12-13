from datetime import datetime
from pprint import pprint

class Messages_Manager():
    def __init__(self):
        self.messages = list()
        self.unread_counter = 0

    def new_message(self, message):
        self.messages.append(message)
        self.unread_counter += 1

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
        found_message = False
        for message in self.messages:
            if message.unread and not found_message:
                found_message = True
                message.unread = False
                self.unread_counter -= 1
        return self.unread_counter


class DisplayMessage():

    def __init__(self, username, message):
        print("Creating new Message")
        self.message = message
        self.length = self.calc_msg_length(message)
        self.username = username
        self.creation_timestamp = datetime.now()
        self.unread = True

    def calc_msg_length(self, message):
        # Initialize with the blank spaces between the letters
        length = len(message) - 1
        for letter in message:
            length += self.calc_length_of_letter(letter)
        print(str(length))
        return length

    def calc_length_of_letter(self, letter):
        #no €, 
        if letter in ["!"]:
            return 1
        if letter in [",", ".", ":", ";", "'"]:
            return 2
        if letter in ["i", "l", "I", str(1), " "]:
            return 3
        elif letter in ["j", "k", "<", ">"]:
            return 4
        else:
            return 5

    def __str__(self) -> str:
        return "From: " + self.username + ": " + self.message
