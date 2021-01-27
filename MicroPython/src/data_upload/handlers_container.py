from machine import Pin
from data_acquisition.data_acquisitor import DataAcquisitor
from network import WLAN


class HandlerContainer:
    def __init__(self):
        self.wlan = None  # type: WLAN
        self.led = None  # type: Pin
        self.data_aquisitor = None  # type: DataAcquisitor

