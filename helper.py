from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
import os

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def make_string_from_list(liste):
    res = ""
    for elem in liste:
        res += str(elem["minutes"]) + ","
    return res[0:-1]

def get_digits(number):
    number: str = str(number)
    digit_list = list()
    for digit in number:
        if digit != "X":
            digit_list.append(int(digit))
        else:
            digit_list.append(digit)
    return digit_list

def get_width(number):
    if isinstance(number, int) or isinstance(number, str):
        number = get_digits(number)
    width = 0
    for digit in number:
        #print("digit: " + str(digit))
        if digit == "X" or (digit > 1 or digit == 0):
            width += 5
        else:
            width += 3
        width += 1 # Space between digits
    return width - 1 # No space after last digit

def get_width_for_multiple_comma_separated_numbers(numbers):
    width = 0
    for number in numbers:
        width += get_width(number)
        width += 4 # comma + free space around it
    return width - 4 # no comma after last digit

#numbers = [45, 30, 31]
#get_width_for_multiple_comma_separated_numbers(numbers)

def get_image_as_list(path, offset_x, offset_y):
        display_list = list()
        with open(path) as picture:
            line = picture.readline()
            x = offset_x
            y = offset_y
            while line:
                line = line.strip()
                for char in line:
                    if char == "*":
                        display_list.append(x)
                        display_list.append(y)
                    x += 1
                line = picture.readline()
                x = offset_x
                y += 1
        return display_list


