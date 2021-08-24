import _thread
import logging

import machine
import utime
from cloud.AWS_cloud import AWS_cloud
from cloud.cloud_interface import CloudProvider, Providers
from cloud.KAA_cloud import KAA_cloud
from cloud.Things_cloud import ThingsBoard
from common import config, utils
from communication import wirerless_connection_controller
from data_acquisition import data_acquisitor
from web_server import web_app

from controller.main_controller_event import (MainControllerEvent,
                                              MainControllerEventType)
from controller.main_controller_state import MainControllerState

ACCESS_POINT_BASE_NAME = "Wizzdev_IoT"
FAILED_TO_MEASURE_VALUE = -99


class MainController:
    """
    MainController is a "scheduler". It should be given every task to perform.
    """
    connection_status = {True: "Connected",
                         False: "Disconnected"}

    last_test_status = {True: "Passed",
                        False: "Failed",
                        None: "No test has been carried out"}

    def __init__(self):
        """
        MainController constructor.
        """
        self.controller_state = MainControllerState()
        self.events_queue = []
        self.lock = _thread.allocate_lock()
        self.data_collector = None
        self.access_point_server = None
        self.is_test_mode_running = False
        self.last_test_result = None
        self.last_test_comment = ""
        self.last_test_end_time = None

        # self.tested_connection_cloud = False
        self.printed_time = False
        self.got_sensor_data = False
        self.published_to_cloud = False

        self.cloud_provider = MainController.get_cloud_provider()

        if config.cfg.cloud_provider == Providers.AWS:
            web_app.setup(get_measurement_hook=self.get_measurement,
                        configure_device_hook=self.cloud_provider.device_configuration,
                        configure_aws_hook=self.cloud_provider.configure_data_from_terraform,
                        configure_sensor_hook=self.configure_sensor,
                        start_test_data_acquisition=self.start_test_data_acquisition_hook,
                        start_data_acquisition=self.start_data_acquisition_hook,
                        get_status_hook=self.get_status)

        elif config.cfg.cloud_provider == Providers.KAA or config.cfg.cloud_provider == Providers.THINGSBOARD :
            web_app.setup(
                get_measurement_hook=self.get_measurement,
                configure_device_hook=self.cloud_provider.device_configuration,
                configure_sensor_hook=self.configure_sensor,
                start_test_data_acquisition=self.start_test_data_acquisition_hook,
                start_data_acquisition=self.start_data_acquisition_hook,
                get_status_hook=self.get_status
            )

        self.web_server_thread = None

        self.data_acquisitor = data_acquisitor.DataAcquisitor()
        logging.debug("FINISHED MAIN CONTROLLER CONSTRUCTOR")

    def add_event(self, event: MainControllerEvent) -> None:
        """
        Adding new task to MainController.
        :param event: New event.
        :return: None
        """
        self.lock.acquire()

        self.events_queue.append(event)
        self.lock.release()

    def perform(self) -> None:
        """
        Executing main loop.
        :return: None
        """
        while True:
            self.lock.acquire()
            if len(self.events_queue) != 0:
                event = self.events_queue.pop(0)
                self.process_event(event)

            self.lock.release()
            utime.sleep_ms(500)

    @staticmethod
    def get_cloud_provider() -> CloudProvider:
        """
        Returns cloud service provider based on current settings in config
        :return: CloudProvider
        """
        if config.cfg.cloud_provider == Providers.AWS:
            return AWS_cloud()
        elif config.cfg.cloud_provider == Providers.KAA:
            return KAA_cloud()
        elif config.cfg.cloud_provider == Providers.THINGSBOARD:
            return ThingsBoard()

    def process_event(self, event: MainControllerEvent) -> None:
        """
        Executing single task based on its type.
        :param event: Task to execute.
        :return: None
        """
        if event.event_type == MainControllerEventType.CONFIGURE_ACCESS_POINT:
            logging.debug("Processing configure access point event")
            access_point_name = "{}_{}".format(
                ACCESS_POINT_BASE_NAME, config.cfg.device_uid)
            logging.debug("Access point name {}".format(access_point_name))

            self.configure_access_point()

        elif event.event_type == MainControllerEventType.TEST_CONNECTION:
            logging.debug("WAITING FOR WIFI CONFIG")
            while not config.cfg.ap_config_done:
                pass
            logging.debug("GOT WIFI CONFIG")
            logging.debug("Testing {} connection".format(config.cfg.cloud_provider))

            MainController.test_connection_with_wifi_and_cloud()

            config.cfg.tested_connection_cloud = True
            config.cfg.save()

        elif event.event_type == MainControllerEventType.PRINT_TIME:
            logging.debug("WAITING FOR TESTED CONNECTION CLOUD")
            while not config.cfg.tested_connection_cloud:
                pass
            logging.debug("GOT TESTED CONNECTION CLOUD")

            self.print_time()
            self.printed_time = True

        elif event.event_type == MainControllerEventType.GET_SENSOR_DATA:
            logging.debug("WAITING FOR PRINTED TIME")
            while not self.printed_time:
                pass
            logging.debug("GOT PRINTED TIME")

            logging.debug("GETTING SENSOR DATA")

            self.data_acquisitor.acquire_temp_humi()
            if not any([FAILED_TO_MEASURE_VALUE in val for (val,) in self.data_acquisitor.data.values()]):
                self.got_sensor_data = True
            else:
                logging.debug("Sensors measured values: {} and {}".format(
                    *self.data_acquisitor.data.values()))

        elif event.event_type == MainControllerEventType.PUBLISH_DATA:
            logging.debug("WAITING FOR GOT SENSOR DATA")
            if self.got_sensor_data:
                logging.debug("GOT SENSOR DATA")
                logging.debug("Publishing data to cloud")
                self.cloud_provider.publish_data(self.data_acquisitor.data)
                self.published_to_cloud = True
            else:
                logging.debug("FAILED GETTING SENSOR DATA")
                logging.debug("Skipping publish...")

        elif event.event_type == MainControllerEventType.GO_TO_SLEEP:

            if self.published_to_cloud:
                logging.debug("WAITING FOR PUBLISHED TO CLOUD")
                logging.debug("GOT PUBLISHED TO CLOUD")

            self.go_to_sleep(event)

        elif event.event_type == MainControllerEventType.ERROR_OCCURRED:
            logging.debug("Processing event error occurred")
            print(event.data)
            self.send_callback(event, True)

        else:
            quit(-1)

    @staticmethod
    def send_callback(event: MainControllerEvent, data: object) -> None:
        """
        Executing event's callback function.
        :param event: Event's object.
        :param data: Callback function parameters.
        :return: None
        """
        if event.callback:
            event.callback(data)

    def get_measurement(self) -> int:
        """
        Get single measurement.
        :return: Value of temperature.
        """
        return self.data_acquisitor.get_single_measurement()

    @staticmethod
    def configure_sensor(sensor_configuration: dict) -> None:
        """
        Create sensor part of config file.
        :param sensor_configuration: Sensor's parameters.
        :return: None.
        """
        logging.debug("Configure sensor")
        print(sensor_configuration)
        if 'publishing_period_ms' in sensor_configuration.keys():
            config.cfg.data_publishing_period_in_ms = int(sensor_configuration['publishing_period_ms'])
        if 'sensor_type' in sensor_configuration.keys():
            config.cfg.sensor_type = sensor_configuration['sensor_type']

    def get_status(self) -> dict:
        """
        Check ESP AP/STA status.
        :return: Status.
        """
        status = {}
        wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()

        status['ap_status'] = self.connection_status[wireless_controller.is_access_point()]
        status['sta_status'] = self.connection_status[wireless_controller.is_station()]
        status['sta_wifi_ssid'] = wireless_controller.get_wifi_ssid()
        status['last_test_status'] = self.last_test_status[self.last_test_result]
        status['last_test_comment'] = self.last_test_comment
        status['last_test_end_time'] = self.last_test_end_time

        return status

    def configure_access_point(self) -> None:
        """
        Configure AP to get wifi ssid and password
        """
        access_point_name = "{}_{}".format(
            ACCESS_POINT_BASE_NAME, config.cfg.device_uid)
        wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
        wireless_controller.configure_access_point(
            access_point_name, "password")
        self.web_server_thread = _thread.start_new_thread(web_app.run, [])

    @staticmethod
    def test_connection_with_wifi_and_cloud() -> None:
        wireless_controller, mqtt_communicator = utils.get_wifi_and_cloud_handlers(
            sync_time=True)

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()

    @staticmethod
    def print_time() -> None:
        time = utime.localtime()
        logging.debug(
            "Actual time: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(time[0], time[1], time[2], time[3], time[4],
                                                                        time[5]))

    def go_to_sleep(self, event: MainControllerEvent) -> None:
        """
        Go to deep sleep.
        """
        # Resets flag before sleep
        self.printed_time = False
        self.got_sensor_data = False
        self.published_to_cloud = False

        logging.debug("sleep({})".format(event.data))
        ms = int(event.data['ms'])
        if ms <= 0:
            ms = 10
        machine.deepsleep(ms)

    def start_test_data_acquisition_hook(self) -> None:
        pass

    def start_data_acquisition_hook(self) -> None:
        pass
