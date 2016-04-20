import time
import re

strip_non_number_regex = re.compile('[^0-9\.,]')


def force_float(x):
    try:
        return float(x)
    except:
        try:
            return float(
                strip_non_number_regex.sub('', x).replace(',', '.'))
        except:
            return None


class timer():
    timers = {}

    @classmethod
    def start(cls, name):
        cls.timers[name] = time.time()

    @classmethod
    def end(cls, name):
        total_time = time.time() - cls.timers[name]
        print('{}: {}s'.format(name, total_time))
        del cls.timers[name]
        return total_time


def split_drops_combines(transforms):
    return [
        filter(lambda x: x['type'] == 'drop', transforms),
        filter(lambda x: x['type'] == 'combine', transforms),
    ]


"""
This was here because of sframe barfing in python 2.7 when trying to access
sframe columns.

def unicode_2str(obj):
    if type(obj) is dict:
        for key in obj:
            obj[key] = unicode_2str(obj[key])
    elif type(obj) is list:
        map(unicode_2str, obj)
    elif type(obj) is unicode:
        obj = str(obj)
    return obj
"""
