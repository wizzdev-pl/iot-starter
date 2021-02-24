import logging
from common import utils
from common import config
from peripherals.dht_sensor import DHTSensor

ADC_TO_VOLTS_ATTN_11DB = 0.000878906
MAX_SAMPLES = 10


class DataAcquisitor:
    """
    Class to collect data from sensor DHT
    """
    def __init__(self):
        self.dht = None
        self.data = {}

        if config.cfg.use_dht:
            self.dht = DHTSensor(dht_type=config.cfg.dht_type,
                                 dht_measurement_pin_number=config.cfg.dht_measurement_pin,
                                 dht_power_pin_number=config.cfg.dht_power_pin)

    def get_data(self) -> None:
        pass

    def acquire_data(self) -> None:
        pass

    def acquire_temp_humi(self) -> dict:
        """
        Get measurements of temperature and humidity.
        :return: Measurements in form of dict
        """
        acquisition_timestamp = utils.get_current_timestamp_ms()
        self.dht.turn_on()
        self.data = {}
        if self.dht is not None:
            try:
                self.dht.measure()
                self.data['dht_t'] = [[acquisition_timestamp, self.dht.temperature()]]
                self.data['dht_h'] = [[acquisition_timestamp + 1, self.dht.humidity()]]
            except OSError:
                logging.info("Error reading DHT sensor!")

        self.dht.turn_off()
        return self.data

    def get_single_measurement(self) -> int:
        """
        Return single measurement of temperature.
        :return: Value of temperature.
        """
        self.dht.turn_on()
        if self.dht is not None:
            try:
                self.dht.measure()
                temperature = self.dht.temperature()
                self.dht.turn_off()
                return temperature
            except OSError:
                logging.error("Error reading DHT sensor!")
                self.dht.turn_off()
                return -1
