
WAKEUP_ALL_LOW = 0
WAKEUP_ANY_HIGH = 1


def wake_on_touch(wake: bool):
    pass


def wake_on_ext0(pin, level):
    pass


def wake_on_ext1(pin,level):
    pass


def raw_temperature() -> int:
    return 0


def hall_sensor() -> int:
    return 0


class Partition():
    BOOT = 0
    RUNNING = 1
    TYPE_APP = 2
    TYPE_DATA = 3

    @classmethod
    def find(type=TYPE_APP, subtype=0xff, label=None):
        pass

    def info(self):
        pass

    def readblocks(self,block_num, buf, offset):
        pass

    def writeblocks(self,block_num, buf, offset):
        pass

    def ioctl(self, cmd, arg):
        pass

    def set_boot(self):
        pass

    def get_next_update(self):
        pass
