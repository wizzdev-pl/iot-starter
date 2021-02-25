from machine import Pin
from network import WLAN

from data_acquisition.data_acquisitor import DataAcquisitor


class HandlerContainer:
    def __init__(self):
        self.wlan = None  # type: WLAN
        self.led = None  # type: Pin
        self.data_aquisitor = None  # type: DataAcquisitor

