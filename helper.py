def make_string_from_list(liste):
    res = ""
    for elem in liste:
        res += str(elem["minutes"]) + ","
    return res[0:-1]

def get_digits(number):
    number: str = str(number)
    digit_list = list()
    for digit in number:
        digit_list.append(int(digit))
    return digit_list

def get_width(number):
    if isinstance(number, int) or isinstance(number, str):
        number = get_digits(number)
    width = 0
    for digit in number:
        if (digit > 1 or digit == 0):
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