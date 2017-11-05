# generate random 10digits phone number
import random


def gen_phone():
    first = "514"
    second = str(random.randint(1, 888)).zfill(3)
    last = (str(random.randint(1, 9998)).zfill(4))
    return '{}-{}-{}'.format(first, second, last)
