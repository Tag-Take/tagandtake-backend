import random
import string


def generate_pin():
    return "".join(random.choices(string.digits, k=4))
