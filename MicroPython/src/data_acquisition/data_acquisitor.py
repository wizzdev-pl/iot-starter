import logging

from common import config, utils
from peripherals.sensor import Sensor

ADC_TO_VOLTS_ATTN_11DB = 0.000878906
MAX_SAMPLES = 10


class DataAcquisitor:
    """
    Class to collect data from sensor
    """

    def __init__(self):
        self.sensor = None
        self.data = {}

        self.sensor = Sensor(sensor_type=config.cfg.sensor_type,
                             sensor_measurement_pin_number=config.cfg.sensor_measurement_pin,
                             sensor_sda_pin_number=config.cfg.sensor_sda_pin, sensor_scl_pin_number=config.cfg.sensor_scl_pin,
                             sensor_power_pin_number=config.cfg.sensor_power_pin)

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
                self.data['temperature'] = [
                    [acquisition_timestamp, self.sensor.temperature()]]
                self.data['humidity'] = [
                    [acquisition_timestamp + 1, self.sensor.humidity()]]
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
