# This module handles all wifi communication

import network
import logging
import time
import ubinascii


wireless_connection_controller_instance = None


def get_wireless_connection_controller_instance():
    # Get global instance of wifi controller, create if not found
    global wireless_connection_controller_instance
    if not wireless_connection_controller_instance:
        wireless_connection_controller_instance = WirelessConnectionController()
    return wireless_connection_controller_instance

def get_mac_address_as_string():
    wlan = network.WLAN()
    mac_address = wlan.config('mac')
    print("Mac address {}".format(mac_address))

    mac_address_string = ubinascii.hexlify(mac_address).decode('asci')
    print("Mac address {}".format(mac_address_string))
    return mac_address_string


class WirelessConnectionController:

    WIFI_CONNECTION_CHECK_SLEEP_TIME_S = 5
    WIFI_CONNECTION_MAX_NUMBER_OF_RETRIES = 10

    def __init__(self, sta_ssid="", sta_password=""):
        self.sta_handler = None
        self.sta_ssid = sta_ssid
        self.sta_password = sta_password
        self.ap_handler = None

    def configure_access_point(self, ssid, password):
        # Configure wifi as access point
        if self.ap_handler:
            return False

        logging.info('About to start Wi-Fi AP: {}, pass: {}'.format(ssid, password))
        self.ap_handler = network.WLAN(network.AP_IF)
        self.ap_handler.active(True)
        self.ap_handler.config(essid=ssid, password=password)

        interface_config = self.ap_handler.ifconfig()
        logging.info('ap_if_config: ' + str(interface_config))

        return True

    def disable_access_point(self):
        if self.ap_handler is not None:
            logging.debug("Disabling AP")
            #self.ap_handler.disconnect()
            self.ap_handler.active(False)

    def setup_station(self, ssid, password):
        # Setup class with parameters to configure device as wifi station by providing
        # ssid and password to external wifi access point
        self.sta_ssid = ssid
        self.sta_password = password

    def configure_station(self):
        # Configure device as wifi station
        if self.sta_handler:
            return False, "STA already connected"

        self.sta_handler = network.WLAN(network.STA_IF)

        if self.sta_handler.isconnected():
            return False, "STA already connected"

        self.sta_handler.active(True)
        existing_networks = self.sta_handler.scan()
        print(existing_networks)
        print("Connect to wifi: {}, pass: {}".format(self.sta_ssid, self.sta_password))
        try:
            self.sta_handler.connect(self.sta_ssid, self.sta_password)
        except:
            return False, "Failed to connect to access point (wifi ssid='{}')".format(self.sta_ssid)

        number_of_retires = 0
        while not self.sta_handler.isconnected():
            logging.info("Reconnection while loop")
            time.sleep(self.WIFI_CONNECTION_CHECK_SLEEP_TIME_S)
            number_of_retires += 1
            if number_of_retires >= self.WIFI_CONNECTION_MAX_NUMBER_OF_RETRIES:
                logging.info("Too many reconnections")
                break


        if self.sta_handler.isconnected():
            self.sta_handler.ifconfig()
            return True, ""
        else:
            self.disconnect_station()
            return False, "Failed to connect to access point v2 (wifi ssid='{}')".format(self.sta_ssid)

    def disconnect_station(self):
        # Disconnect wifi station
        if not self.sta_handler:
            return True
        #self.sta_handler.disconnect()
        self.sta_handler.active(False)
        self.sta_handler = None
        return True

    def is_station(self):
        # Check if wifi is configured as station
        return self.sta_handler is not None

    def is_access_point(self):
        # Check if wifi is configured as access point
        return self.ap_handler is not None

    def get_wifi_ssid(self):
        # Get ssid to which station is connected
        return self.sta_ssid
