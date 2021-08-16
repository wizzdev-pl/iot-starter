import network
import logging
import time
import ubinascii

wireless_connection_controller_instance = None


class WirelessConnectionController:
    """
    Wifi handler class.
    """
    WIFI_CONNECTION_CHECK_SLEEP_TIME_S = 5
    WIFI_CONNECTION_MAX_NUMBER_OF_RETRIES = 10

    def __init__(self, sta_ssid: str = "", sta_password: str = ""):
        """
        Constructor of WirelessConnectionController class.
        :param sta_ssid: Wifi ssid.
        :param sta_password: Wifi password.
        """
        self.sta_handler = None
        self.sta_ssid = sta_ssid
        self.sta_password = sta_password
        self.ap_handler = None

    def configure_access_point(self, ssid: str, password: str) -> bool:
        """
        Configure Access Point with given ssid and password
        :param ssid: AP ssid.
        :param password: AP password.
        :return: Error code (True - OK, False - error).
        """
        if self.ap_handler:
            return False

        logging.info('About to start Wi-Fi AP: {}, pass: {}'.format(ssid, password))
        self.ap_handler = network.WLAN(network.AP_IF)
        self.ap_handler.active(True)
        self.ap_handler.config(essid=ssid, password=password)

        interface_config = self.ap_handler.ifconfig()
        logging.info('ap_if_config: ' + str(interface_config))

        return True

    def disable_access_point(self) -> None:
        """
        Disable/Turn off Access Point.
        :return: None.
        """
        if self.ap_handler is not None:
            logging.debug("Disabling AP")
            self.ap_handler.active(False)

    def setup_station(self, access_points: list[dict]) -> None:
        """
        Change default ssid and password to given ones.
        :param access_points: list of ssid & password pairs
        :return: None.
        """
        self.sta_access_points = access_points

    def configure_station(self) -> (bool, str):
        """
        Configuration of wifi station.
        :return: Error code (True - OK, False - Error), error message.
        """
        if self.sta_handler:
            raise Exception("STA Already connected")

        self.sta_handler = network.WLAN(network.STA_IF)

        if self.sta_handler.isconnected():
            raise Exception("STA Already connected")

        self.sta_handler.active(True)
        existing_networks = self.sta_handler.scan()

        # Sort detected networks according to signal strength in descending order and filter out the ones to
        # which credentials were not given
        existing_networks.sort(reverse=True, key=lambda ap: ap[3])
        logging.info("Networks detected: {}".format(existing_networks))

        existing_networks_also_on_AP_list_sorted = []
        for ap in existing_networks:
            for credential_pair in self.sta_access_points:
                if ap[0].decode('ascii') == credential_pair[
                    "ssid"] and ap not in existing_networks_also_on_AP_list_sorted:
                    existing_networks_also_on_AP_list_sorted.append(ap)

        logging.info("Networks detected that are also on AP ssid & password list: {}".format(
            existing_networks_also_on_AP_list_sorted))

        for ap in existing_networks_also_on_AP_list_sorted:

            # There could be many SSID & Password pairs saved for a single network therefore a list
            # of pairs is used and looped over instead of a single SSID & Password pair variable
            credentials_for_ap = []

            for credential_pair in self.sta_access_points:
                if ap[0].decode('ascii') == credential_pair["ssid"]:
                    credentials_for_ap.append(credential_pair)

            for credential_pair in credentials_for_ap:

                print(
                    "Connecting to wifi: {}, pass: {}".format(credential_pair["ssid"],
                                                              credential_pair["password"]))
                try:
                    self.sta_handler.connect(credential_pair["ssid"], credential_pair["password"])
                except Exception:
                    raise Exception(
                        "Failed to connect to access point (wifi ssid='{}')".format(credential_pair["ssid"]))

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
                    logging.info("Failed to connect to AP: {}".format(credential_pair["ssid"]))
        self.disconnect_station()
        raise Exception("Failed to connect to any AP")

    def disconnect_station(self) -> bool:
        """
        Disconnects wifi station.
        :return: Error code (True - OK, False - Error).
        """
        if not self.sta_handler:
            return True
        self.sta_handler.active(False)
        self.sta_handler = None
        return True

    def is_station(self) -> bool:
        """
        Check if device is setup as station.
        :return: True -> device is wifi station, False -> station is not wifi station.
        """
        return self.sta_handler is not None

    def is_access_point(self) -> bool:
        """
        Check if device is setup as access point.
        :return: True -> device is access point, False -> station is not access point.
        """
        return self.ap_handler is not None

    def get_wifi_ssid(self) -> str:
        """
        Gets wifi station ssid.
        :return: Wifi ssid.
        """
        return self.sta_ssid


def get_wireless_connection_controller_instance() -> WirelessConnectionController:
    """
    Get wifi handler or create it and get it.
    :return: Wifi handler.
    """
    global wireless_connection_controller_instance
    if not wireless_connection_controller_instance:
        wireless_connection_controller_instance = WirelessConnectionController()
    return wireless_connection_controller_instance


def get_mac_address_as_string() -> str:
    """
    Get MAC address as string.
    :return: MAC address.
    """
    wlan = network.WLAN()
    mac_address = wlan.config('mac')
    print("Mac address {}".format(mac_address))

    mac_address_string = ubinascii.hexlify(mac_address).decode('asci')
    print("Mac address {}".format(mac_address_string))
    return mac_address_string
