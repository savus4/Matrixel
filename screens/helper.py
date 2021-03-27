def calc_string_length(message):
    # Initialize with the blank spaces between the letters
    length = len(message) - 1
    for letter in message:
        length += calc_length_of_letter(letter)
    #print(str(length))
    return length

def calc_length_of_letter(letter):
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