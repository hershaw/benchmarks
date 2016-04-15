import time


class timer():
    timers = {}

    @classmethod
    def start(cls, name):
        cls.timers[name] = time.time()

    @classmethod
    def end(cls, name):
        print('{}: {}s'.format(name, time.time() - cls.timers[name]))
        del cls.timers[name]


def split_drops_combines(transforms):
    return [
        filter(lambda x: x['type'] == 'drop', transforms),
        filter(lambda x: x['type'] == 'combine', transforms),
    ]
