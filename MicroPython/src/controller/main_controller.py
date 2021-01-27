from _thread import allocate_lock
from controller.main_controller_state import MainControllerState
from controller.main_controller_event import MainControllerEvent, MainControllerEventType
from data_acquisition import data_acquisitor
from data_acquisition import run_test_data_acquisition
from common import config, utils
from communication.API_communication import authorization_request, configuration_request


import logging
import utime
import machine
import gc

from communication import wirerless_connection_controller
from web_server import web_app

import _thread

ACCESS_POINT_BASE_NAME = "Wizzdev_IoT"

class MainController():
    connection_status = {True: "Connected",
                         False: "Disconnected"}

    last_test_status = {True: "Passed",
                        False: "Failed",
                        None: "No test has been carried out"}

    def __init__(self):
        self.controller_state = MainControllerState()
        self.events_queue = []
        self.lock = allocate_lock()
        self.data_collector = None
        self.access_point_server = None
        self.is_test_mode_running = False
        self.last_test_result = None
        self.last_test_comment = ""
        self.last_test_end_time = None

        web_app.setup(get_measurement_hook=self.get_measurement,
                      configure_device_hook=self.device_configuration,
                      configure_aws_hook=self.configure_data_from_terraform,
                      configure_sensor_hook=self.configure_sensor,
                      start_test_data_acquisition=self.start_test_data_acquisition_hook,
                      start_data_acquisition=self.start_data_acquisition_hook,
                      get_status_hook=self.get_status)
        self.web_server_thread = None

        self.data_acquisitor = data_acquisitor.DataAcquisitor()

    def add_event(self, event: MainControllerEvent):
        self.lock.acquire()

        self.events_queue.append(event)
        self.lock.release()

    def perform(self):
        while True:
            self.lock.acquire()
            if len(self.events_queue) != 0:
                event = self.events_queue.pop(0)
                self.process_event(event)

            self.lock.release()
            utime.sleep_ms(500)

    def process_event(self, event: MainControllerEvent):
        if event.event_type == MainControllerEventType.CONFIGURE_ACCESS_POINT:
            logging.debug("Processing configure access point event")
            access_point_name = "{}_{}".format(ACCESS_POINT_BASE_NAME, config.cfg.device_uid)
            logging.debug("Access point name {}".format(access_point_name))

            wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
            wireless_controller.configure_access_point(access_point_name, "password")
            self.web_server_thread = _thread.start_new_thread(web_app.run, [])

        elif event.event_type == MainControllerEventType.START_DATA_ACQUISITION:
            logging.debug("Processing event start data acquisition")
            wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
            wireless_controller.disconnect_station()
            wireless_controller.disable_access_point()
            config.cfg.save_to_file()
            utils.set_ap_config_done(True)
            machine.reset()
            self.send_callback(event, True)

        elif event.event_type == MainControllerEventType.START_TEST_DATA_ACQUISITION:
            logging.debug("Processing event start test data acquisition")
            # result = self.data_collector.start_data_acquisition(event.data)
            self.is_test_mode_running = True
            result = run_test_data_acquisition.schedule_test_mode(self.data_acquisitor)
            self.last_test_end_time = utime.time()
            if result[0]:
                logging.debug("Test processing finished successfully")
            else:
                logging.error("Failed to run test data acquisition {}".format(result[1]))

            self.last_test_comment = result[1]
            self.last_test_result = result[0]

            self.is_test_mode_running = False
            self.send_callback(event, True)

        elif event.event_type == MainControllerEventType.ERROR_OCCURRED:
            logging.debug("Processing event error occurred")
            print(event.data)
            self.event_handler(event.data)
            self.send_callback(event, True)

        else:
            quit(-1)

    def event_handler(self, *event_data):
        pass

    @staticmethod
    def send_callback(event, data):
        if event.callback:
            event.callback(data)

    def get_measurement(self):
        return self.data_acquisitor.get_single_measurement()

    def device_configuration(self, data):
        ssid = data['ssid']
        password = data['password']
        config.cfg.password = password
        config.cfg.ssid = ssid
        config.cfg.save_to_file()
        logging.info("Wifi config. Wifi ssid {} Wifi password {}".format(ssid, password))

        wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
        #TODO some handling of bad password
        utils.connect_to_wifi(wireless_controller)
        logging.info(wireless_controller.sta_handler.ifconfig())
        try:
            self.configure_aws_thing()
        except Exception as e:
            logging.error("Exception catched: {}".format(e))
            event = MainControllerEvent(MainControllerEventType.ERROR_OCCURRED)
            self.add_event(event)
            return None

        event = MainControllerEvent(MainControllerEventType.START_DATA_ACQUISITION, None)
        self.add_event(event)

    def configure_aws_thing(self):
        logging.info("Allocated bytes on heap before gc {}".format(gc.mem_alloc()))
        gc.collect()
        logging.info("Allocated bytes on heap after gc {}".format(gc.mem_alloc()))
        self.configure_data_from_terraform()
        logging.debug("Authorization request...")
        jwt_token = authorization_request()

        if jwt_token is not None:
            cert_dict = configuration_request(jwt_token)
            config.save_certificates(cert_dict)
            logging.debug("Configuration done")
            return True
        else:
            logging.error("Problem with authorization")
            event = MainControllerEvent(MainControllerEventType.ERROR_OCCURRED)
            self.add_event(event)
            return False

    def configure_data_from_terraform(self):
        logging.debug("configure_data_from_terraform")
        aws_configuration = config.cfg.load_aws_config_from_file()
        if 'aws_iot_endpoint' in aws_configuration.keys():
            config.cfg.aws_endpoint = aws_configuration['aws_iot_endpoint'].get("value").get("endpoint_address")

        if 'visualization_url' in aws_configuration.keys():
            visualization_url = aws_configuration['visualization_url'].get("value")
            config.cfg.api_url = 'https://' + visualization_url + '/api/'

        if 'esp_login' in aws_configuration.keys():
            config.cfg.api_login = aws_configuration['esp_login'].get("value")

        if 'esp_password' in aws_configuration.keys():
            config.cfg.api_password = aws_configuration['esp_password'].get("value")

        config.cfg.save_to_file()

        logging.debug("Configure data from terraform ends")

    def configure_sensor(self, sensor_configuration):
        logging.debug("Configure sensor")
        print(sensor_configuration)
        if 'acquisition_period_ms' in sensor_configuration.keys():
            config.cfg.data_aqusition_period_in_ms = int(sensor_configuration['acquisition_period_ms'])
        if 'publishing_period_ms' in sensor_configuration.keys():
            config.cfg.data_publishing_period_in_ms = int(sensor_configuration['publishing_period_ms'])
        if 'dht_type' in sensor_configuration.keys():
            config.cfg.dht_type = sensor_configuration['dht_type']
        if 'blink_led' in sensor_configuration.keys():
            config.cfg.blink_led = sensor_configuration['blink_led']

    def get_status(self):
        status = {}
        wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()

        status['ap_status'] = self.connection_status[wireless_controller.is_access_point()]
        status['sta_status'] = self.connection_status[wireless_controller.is_station()]
        status['sta_wifi_ssid'] = wireless_controller.get_wifi_ssid()
        status['last_test_status'] = self.last_test_status[self.last_test_result]
        status['last_test_comment'] = self.last_test_comment
        status['last_test_end_time'] = self.last_test_end_time

        return status

    def start_test_data_acquisition_hook(self):
        event = MainControllerEvent(MainControllerEventType.START_TEST_DATA_ACQUISITION, None)
        self.add_event(event)

    def start_data_acquisition_hook(self):
        event = MainControllerEvent(MainControllerEventType.START_DATA_ACQUISITION, None)
        self.add_event(event)

