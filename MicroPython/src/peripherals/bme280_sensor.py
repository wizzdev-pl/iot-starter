import dht
import utime
import machine
import logging
import lib.bme280 as bme280


TIME_TO_BME280_TO_WAKE_UP_S = 0 # not sure if necessary

FAILED_TO_MEASURE_VALUE = -99


class BME280Sensor:
    """
    Class to wrap function to communicate with sensor
    """
    def __init__(self, bme280_sda_pin_number, bme280_scl_pin_number, bme280_power_pin_number):
        """
        Constructor.
        :param bme280_sda_pin_number: Number which indicates to which pin sensor's SDA pin is connected.
        :param bme280_scl_pin_number: Number which indicates to which pin sensor's SCL pin is connected.
        """
        logging.debug("Sensor.__init__()")
        self.bme280_sda_pin = machine.Pin(bme280_sda_pin_number)
        self.bme280_scl_pin = machine.Pin(bme280_scl_pin_number)
        self.bme280_power_pin = machine.Pin(bme280_power_pin_number, machine.Pin.OUT)
        self.bme280_power_on = False
        self.bme280_last_measure_status = False
        self.i2c = machine.I2C(scl=self.bme280_scl_pin, sda=self.bme280_sda_pin, freq=100000)
        self.bme280 = None

    def measure(self) -> None:
        """
        Measure.
        :return: None
        """
        logging.debug("Sensor.measure()")
        try:
            #self.bme280._load_calibration()
            self.bme280 = bme280.BME280(i2c=self.i2c)
            self.bme280_last_measure_status = True
        except OSError:
            logging.error("Error while sensor measure. Check if your sensor is connected correctly")
            self.bme280_last_measure_status = False

    def humidity(self) -> float:
        """
        Get humidity.
        :return: Humidity
        """
        if self.bme280_last_measure_status:
            logging.debug("BME280Sensor.humidity() = {}".format(self.bme280.humidity))
            return self.bme280.humidity
        else:
            logging.debug("BME280Sensor.humidity() = {}".format(FAILED_TO_MEASURE_VALUE))
            return FAILED_TO_MEASURE_VALUE

    def temperature(self) -> float:
        """
        Get temperature.
        :return: Temperature
        """
        if self.bme280_last_measure_status:
            logging.debug("BME280Sensor.temperature() = {}".format(self.bme280.temperature))
            return self.bme280.temperature
        else:
            logging.debug("BME280Sensor.temperature() = {}".format(FAILED_TO_MEASURE_VALUE))
            return FAILED_TO_MEASURE_VALUE

    def turn_on(self) -> None:
        """
        Turn on the sensor.
        :return: None
        """
        logging.debug("BME280Sensor.turn_on()")
        if not self.bme280_power_on:
            self.bme280_power_pin.on()
            utime.sleep(TIME_TO_BME280_TO_WAKE_UP_S)
            self.bme280_power_on = True

    def turn_off(self) -> None:
        """
        Turn off the sensor.
        :return: None
        """
        logging.debug("BME280Sensor.turn_off()")
        if self.bme280_power_on:
            self.bme280_power_pin.off()
            self.bme280_power_on = False
