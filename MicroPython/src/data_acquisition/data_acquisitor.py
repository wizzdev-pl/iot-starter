import dht
import logging
import machine

from common import utils
from common import config
from peripherals.dht_sensor import DHTSensor

ADC_TO_VOLTS_ATTN_11DB = 0.000878906
MAX_SAMPLES = 10


class DataAcquisitor:
    data_storage = {}

    def __init__(self):
        self.dht = None

        if config.cfg.use_dht:
            self.data_storage['dht'] = []
            self.dht = DHTSensor(dht_type=config.cfg.dht_type,
                                 dht_measurement_pin_number=config.cfg.dht_measurement_pin,
                                 dht_power_pin_number=config.cfg.dht_power_pin)

    def get_data(self):
        return self.data_storage

    def acquire_data(self):
        acquisition_timestamp = utils.get_current_timestamp_ms()
        self.dht.turn_on()
        if self.dht is not None:
            try:
                self.dht.measure()
                dht_entry = (acquisition_timestamp, self.dht.temperature(), self.dht.humidity())
                if len(self.data_storage['dht']) < MAX_SAMPLES:
                    self.data_storage['dht'].append(dht_entry)
                else:
                    self.data_storage['dht'].pop(0)
                    self.data_storage['dht'].append(dht_entry)
            except OSError:
                logging.info("Error reading DHT sensor!")
        self.dht.turn_off()

    def get_single_measurement(self):
        self.dht.turn_on()
        if self.dht is not None:
            try:
                self.dht.measure()
                temperature = self.dht.temperature()
                self.dht.turn_off()
                return temperature
            except OSError:
                logging.info("Error reading DHT sensor!")
                self.dht.turn_off()
                return -1
