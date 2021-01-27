# IRQ Wake Values
IDLE = 0
SLEEP = 1
DEEPSLEEP = 2

# Reset Causes
PWRON_RESET = 0
SOFT_RESET = 1
HARD_RESET = 2
WDT_RESET = 3
DEEPSLEEP_RESET = 4


# Wake-up Reasons
EXT0_WAKE = 2
EXT1_WAKE = 3
PIN_WAKE = 2
TIMER_WAKE = 4
TOUCHPAD_WAKE = 5
ULP_WAKE = 6


class ADC:
    ATTN_0DB = 0
    ATTN_11DB = 1
    ATTN_2_5DB = 2
    ATTN_6DB = 3
    WIDTH_10BIT = 4
    WIDTH_11BIT = 5
    WIDTH_12BIT = 6
    WIDTH_9BIT = 7

    def __init__(self, pin):
        pass

    def read(self):
        return 1.65

    def atten(self, attenuation):
        pass

    def width(self, width):
        pass


class Pin:
    IN = 0
    OUT = 1

    def __init__(self, pin_num, pin_dir=None):
        pass

    def on(self):
        pass

    def off(self):
        pass


class SDCard:
    def __init__(self, slot, width=1):
        pass


class Timer:
    def __init__(self, id):
        pass


def deepsleep(time_to_sleep):
    pass


def lightsleep(time_to_sleep):
    pass


def reset_cause():
    return 0


def wake_reason():
    return 0


def unique_id():
    return 0


def reset():
    pass