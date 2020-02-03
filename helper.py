def make_string_from_list(list):
    res = ""
    for elem in list:
        res += str(elem) + ", "
    return res[0:-2]

