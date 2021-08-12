import dht
import utime
import machine
import logging
import lib.bme280 as bme280

TIME_TO_DHT11_TO_WAKE_UP_S = 1
TIME_TO_DHT22_TO_WAKE_UP_S = 0.5
TIME_TO_BME280_TO_WAKE_UP_S = 0.5

FAILED_TO_MEASURE_VALUE = -99


class Sensor:
    """
    Class to wrap function to communicate with sensor
    """
    def __init__(self, sensor_type, sensor_measurement_pin_number, 
                sensor_sda_pin_number, sensor_scl_pin_number, sensor_power_pin_number):
        """
        Constructor.
        :param sensor_type: Type of sensor.
        :param sensor_measurement_pin_number: Number which indicates to which pin sensor's data pin is connected.
        :param sensor_sda_pin_number: Number which indicates to which pin sensor's SDA pin is connected.
        :param sensor_scl_pin_number: Number which indicates to which pin sensor's SCL pin is connected.
        :param sensor_power_pin_number: Number which indicates to which pin sensor's power pin is connected.
        """
        logging.debug("Sensor.__init__()")
        self.sensor_type = sensor_type
        self.sensor_power_pin = machine.Pin(sensor_power_pin_number, machine.Pin.OUT)
        self.sensor_power_on = False
        self.sensor_last_measure_status = False

        if self.sensor_type == "DHT11":
            self.sensor_measurement_pin = sensor_measurement_pin_number
            self.sensor = dht.DHT11(machine.Pin(sensor_measurement_pin_number))
        elif self.sensor_type == "DHT22":
            self.sensor_measurement_pin = sensor_measurement_pin_number
            self.sensor = dht.DHT22(machine.Pin(sensor_measurement_pin_number))
        elif self.sensor_type == "BME280":
            self.sensor_sda_pin = machine.Pin(sensor_sda_pin_number)
            self.sensor_scl_pin = machine.Pin(sensor_scl_pin_number)
            self.i2c = machine.I2C(scl=self.sensor_scl_pin, sda=self.sensor_sda_pin, freq=100000)
            self.sensor = bme280.BME280(i2c=self.i2c)
        else:
            raise Exception("Wrong sensor type provided! " + self.sensor_type + " is not supported")
        
        
    def measure(self) -> None:
        """
        Measure.
        :return: None
        """
        logging.debug("Sensor.measure()")
        # Trying to measure up to three times by the possibility of error while reading sensor
        for _ in range(3):
            try:
                self.sensor.measure()
                self.sensor_last_measure_status = True
            except OSError:
                continue
            break
        else:
            logging.error("Error while sensor measure. Check if your sensor is connected correctly")
            self.sensor_last_measure_status = False

    def humidity(self) -> float:
        """
        Get humidity.
        :return: Humidity
        """
        if self.sensor_last_measure_status:
            logging.debug("Sensor.humidity() = {}".format(self.sensor.humidity()))
            return self.sensor.humidity()
        else:
            logging.debug("Sensor.humidity() = {}".format(FAILED_TO_MEASURE_VALUE))
            return FAILED_TO_MEASURE_VALUE

    def temperature(self) -> float:
        """
        Get temperature.
        :return: Temperature
        """
        if self.sensor_last_measure_status:
            logging.debug("Sensor.temperature() = {}".format(self.sensor.temperature()))
            return self.sensor.temperature()
        else:
            logging.debug("Sensor.temperature() = {}".format(FAILED_TO_MEASURE_VALUE))
            return FAILED_TO_MEASURE_VALUE

    def turn_on(self) -> None:
        """
        Turn on the sensor.
        :return: None
        """
        logging.debug("Sensor.turn_on()")
        if not self.sensor_power_on:
            self.sensor_power_pin.on()
            if self.sensor_type == "DHT22":
                utime.sleep(TIME_TO_DHT22_TO_WAKE_UP_S)
            elif self.sensor_type == "DHT11":
                utime.sleep(TIME_TO_DHT11_TO_WAKE_UP_S)
            elif self.sensor_type == "BME280":
                utime.sleep(TIME_TO_BME280_TO_WAKE_UP_S)
            self.sensor_power_on = True

    def turn_off(self) -> None:
        """
        Turn off the sensor.
        :return: None
        """
        logging.debug("Sensor.turn_off()")
        if self.sensor_power_on:
            self.sensor_power_pin.off()
            self.sensor_power_on = False
