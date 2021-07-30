import logging

from common import utils
from common import config
from peripherals.dht_sensor import DHTSensor
from peripherals.bme280_sensor import BME280Sensor

ADC_TO_VOLTS_ATTN_11DB = 0.000878906
MAX_SAMPLES = 10


class DataAcquisitor:
    """
    Class to collect data from sensor
    """
    def __init__(self):
        self.sensor = None
        self.data = {}

        if config.cfg.use_dht:
            self.sensor = DHTSensor(dht_type=config.cfg.dht_type,
                                 dht_measurement_pin_number=config.cfg.dht_measurement_pin,
                                 dht_power_pin_number=config.cfg.sensor_power_pin)
        else:
            self.sensor = BME280Sensor(bme280_sda_pin_number=config.cfg.bme280_sda_pin, 
                                    bme280_scl_pin_number=config.cfg.bme280_scl_pin, 
                                    bme280_power_pin_number=config.cfg.sensor_power_pin)

    def acquire_temp_humi(self) -> dict:
        """
        Get measurements of temperature and humidity.
        :return: Measurements in form of dict
        """
        acquisition_timestamp = utils.get_current_timestamp_ms()
        self.sensor.turn_on()
        self.data = {}
        if self.sensor is not None:
            try:
                self.sensor.measure()
                self.data['temperature'] = [[acquisition_timestamp, self.sensor.temperature()]]
                self.data['humidity'] = [[acquisition_timestamp + 1, self.sensor.humidity()]]
            except OSError:
                logging.info("Error reading sensor!")

        self.sensor.turn_off()
        return self.data

    def get_single_measurement(self) -> int:
        """
        Return single measurement of temperature.
        :return: Value of temperature.
        """
        self.sensor.turn_on()
        if self.sensor is not None:
            try:
                self.sensor.measure()
                temperature = self.sensor.temperature()
                self.sensor.turn_off()
                return temperature
            except OSError:
                logging.error("Error reading sensor!")
                self.sensor.turn_off()
                return -1
