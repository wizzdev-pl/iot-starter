import dht
import utime
import machine
import logging

TIME_TO_DHT11_TO_WAKE_UP_S = 1
TIME_TO_DHT22_TO_WAKE_UP_S = 0.5

FAILED_TO_MEASURE_VALUE = -99


class DHTSensor:
    """
    Class to wrap function to communicate with sensor
    """
    def __init__(self, dht_type, dht_measurement_pin_number, dht_power_pin_number):
        """
        Constructor.
        :param dht_type: Type of sensor.
        :param dht_measurement_pin_number: Number which indicates to which pin sensor's data pin is connected.
        :param dht_power_pin_number: Number which indicates to which pin sensor's power pin is connected.
        """
        logging.debug("DHTSensor.__init__()")
        self.dht_type = dht_type
        self.dht_measurement_pin = dht_measurement_pin_number
        self.dht_power_pin = machine.Pin(dht_power_pin_number, machine.Pin.OUT)
        self.dht_powered_on = False
        self.dht_last_measure_status = False

        if self.dht_type == "DHT22":
            self.dht = dht.DHT22(machine.Pin(dht_measurement_pin_number))
        elif self.dht_type == "DHT11":
            self.dht = dht.DHT11(machine.Pin(dht_measurement_pin_number))

    def measure(self) -> None:
        """
        Measure.
        :return: None
        """
        logging.debug("DHTSensor.measure()")
        try:
            self.dht.measure()
            self.dht_last_measure_status = True
        except OSError:
            logging.error("Error while DHT measure. Check if your sensor is connected correctly")
            self.dht_last_measure_status = False

    def humidity(self) -> float:
        """
        Get humidity.
        :return: Humidity
        """
        if self.dht_last_measure_status:
            logging.debug("DHTSensor.humidity() = {}".format(self.dht.humidity()))
            return self.dht.humidity()
        else:
            logging.debug("DHTSensor.humidity() = {}".format(FAILED_TO_MEASURE_VALUE))
            return FAILED_TO_MEASURE_VALUE

    def temperature(self) -> float:
        """
        Get temperature.
        :return: Temperature
        """
        if self.dht_last_measure_status:
            logging.debug("DHTSensor.temperature() = {}".format(self.dht.temperature()))
            return self.dht.temperature()
        else:
            logging.debug("DHTSensor.temperature() = {}".format(FAILED_TO_MEASURE_VALUE))
            return FAILED_TO_MEASURE_VALUE

    def turn_on(self) -> None:
        """
        Tern on the sensor.
        :return: None
        """
        logging.debug("DHTSensor.turn_on()")
        if not self.dht_powered_on:
            self.dht_power_pin.on()
            if self.dht_type == "DHT22":
                utime.sleep(TIME_TO_DHT22_TO_WAKE_UP_S)
            elif self.dht_type == "DHT11":
                utime.sleep(TIME_TO_DHT11_TO_WAKE_UP_S)
            self.dht_powered_on = True

    def turn_off(self) -> None:
        """
        Turn off the sensor.
        :return: None
        """
        logging.debug("DHTSensor.turn_off()")
        if self.dht_powered_on:
            self.dht_power_pin.off()
            self.dht_powered_on = False

