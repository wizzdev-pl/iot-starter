import time as org_time


_t0 = org_time.time()


def time():
    return int(org_time.time() - _t0)


def ticks_ms():
    return int((org_time.time() - _t0) * 1000)


def localtime():
    pass

def mktime():
    pass


def sleep(value):
    org_time.sleep(value)


def sleep_ms():
    pass


def sleep_us():
    pass


def ticks_add():
    pass


def ticks_cpu():
    pass


def ticks_diff():
    pass


def ticks_us():
    pass


