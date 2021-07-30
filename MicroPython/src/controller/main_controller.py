import _thread
import logging
import utime
import machine
import gc

from common import config, utils
from web_server import web_app
from data_acquisition import data_acquisitor
from communication import wirerless_connection_controller
from controller.main_controller_state import MainControllerState
from controller.main_controller_event import MainControllerEvent, MainControllerEventType

ACCESS_POINT_BASE_NAME = "Wizzdev_IoT"


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

        web_app.setup(get_measurement_hook=self.get_measurement,
                      configure_device_hook=self.device_configuration,
                      configure_aws_hook=self.configure_data_from_terraform,
                      configure_sensor_hook=self.configure_sensor,
                      start_test_data_acquisition=self.start_test_data_acquisition_hook,
                      start_data_acquisition=self.start_data_acquisition_hook,
                      get_status_hook=self.get_status)
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

    def process_event(self, event: MainControllerEvent) -> None:
        """
        Executing single task based on its type.
        :param event: Task to execute.
        :return: None
        """
        if event.event_type == MainControllerEventType.CONFIGURE_ACCESS_POINT:
            logging.debug("Processing configure access point event")
            access_point_name = "{}_{}".format(ACCESS_POINT_BASE_NAME, config.cfg.device_uid)
            logging.debug("Access point name {}".format(access_point_name))

            self.configure_access_point()

        elif event.event_type == MainControllerEventType.TEST_CONNECTION:
            logging.debug("WAITING FOR WIFI CONFIG")
            while not config.cfg.ap_config_done:
                pass
            logging.debug("GOT WIFI CONFIG")
            logging.debug("Testing AWS connection")

            MainController.test_connection_with_wifi_and_cloud()

            config.cfg.tested_connection_cloud = True
            config.cfg.save()

        elif event.event_type == MainControllerEventType.PRINT_TIME:
            logging.debug("WAITING FOR TESTED CONNECTION CLOUD")
            while not config.cfg.tested_connection_cloud:
                pass
            logging.debug("GOT TESTED CONNECTION CLOUD")

            self.print_time()

            config.cfg.printed_time = True
            config.cfg.save()

        elif event.event_type == MainControllerEventType.GET_SENSOR_DATA:
            logging.debug("WAITING FOR PRINTED TIME")
            while not config.cfg.printed_time:
                pass
            logging.debug("GOT PRINTED TIME")

            logging.debug("GETTING SENSOR DATA")

            self.data_acquisitor.acquire_temp_humi()

            config.cfg.got_sensor_data = True
            config.cfg.save()

        elif event.event_type == MainControllerEventType.PUBLISH_DATA:
            logging.debug("WAITING FOR GOT SENSOR DATA")
            while not config.cfg.got_sensor_data:
                pass
            logging.debug("GOT GOT SENSOR DATA")
            logging.debug("Publishing data to cloud")

            self.publish_data()

            config.cfg.published_to_cloud = True
            config.cfg.save()

        elif event.event_type == MainControllerEventType.GO_TO_SLEEP:
            logging.debug("WAITING FOR PUBLISHED TO CLOUD")
            while not config.cfg.published_to_cloud:
                pass
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

    def device_configuration(self, data: dict) -> int:
        """
        Configures device in the cloud. Function used as hook to web_app.
        :param data: parameters to connect to wifi.
        :return: Error code (0 - OK, 1 - Error).
        """
        ssid = data['ssid']
        password = data['password']
        config.cfg.password = password
        config.cfg.ssid = ssid
        config.cfg.save()
        logging.info("Wifi config. Wifi ssid {} Wifi password {}".format(ssid, password))

        wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
        try:
            utils.connect_to_wifi(wireless_controller)
            logging.info(wireless_controller.sta_handler.ifconfig())
            self.configure_aws_thing()
        except Exception as e:
            logging.error("Exception catched: {}".format(e))
            event = MainControllerEvent(MainControllerEventType.ERROR_OCCURRED)
            self.add_event(event)
            return 1

        config.cfg.ap_config_done = True
        config.cfg.save()
        machine.reset()
        return 0

    def configure_aws_thing(self) -> bool:
        """
        Register ESP as thing in AWS cloud.
        :return: Error code (True - OK, False - Error).
        """
        logging.info("Allocated bytes on heap before gc {}".format(gc.mem_alloc()))
        gc.collect()
        logging.info("Allocated bytes on heap after gc {}".format(gc.mem_alloc()))
        self.configure_data_from_terraform()
        logging.debug("Authorization request...")
        jwt_token = config.ESPConfig.authorization_request()

        if jwt_token is not "":
            cert_dict = config.ESPConfig.configuration_request(jwt_token)
            config.ESPConfig.save_certificates(cert_dict)
            logging.debug("Configuration done")
            return True
        else:
            logging.error("Problem with authorization")
            event = MainControllerEvent(MainControllerEventType.ERROR_OCCURRED)
            self.add_event(event)
            return False

    @staticmethod
    def configure_data_from_terraform() -> None:
        """
        Setup data from terraform to connect to AWS.
        :return: None
        """
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

        config.cfg.save()

        logging.debug("Configure data from terraform ends")

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
        if 'dht_type' in sensor_configuration.keys():
            config.cfg.dht_type = sensor_configuration['dht_type']

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
        access_point_name = "{}_{}".format(ACCESS_POINT_BASE_NAME, config.cfg.device_uid)
        wireless_controller = wirerless_connection_controller.get_wireless_connection_controller_instance()
        wireless_controller.configure_access_point(access_point_name, "password")
        self.web_server_thread = _thread.start_new_thread(web_app.run, [])

    @staticmethod
    def test_connection_with_wifi_and_cloud() -> None:
        wireless_controller, mqtt_communicator = utils.get_wifi_and_aws_handlers(sync_time=True)

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()

    def publish_data(self) -> None:
        """
        Publish data to the cloud
        """
        wireless_controller, mqtt_communicator = utils.get_wifi_and_aws_handlers(sync_time=False)

        certificates_existence, *_ = config.ESPConfig.read_certificates()
        if not certificates_existence:
            logging.debug("No AWS Certificates, configure_aws_thing()")
            self.configure_aws_thing()

        logging.debug("data to send = {}".format(self.data_acquisitor.data))
        logging.info(config.cfg.aws_topic)
        result = mqtt_communicator.publish_message(payload=self.data_acquisitor.data, topic=config.cfg.aws_topic,
                                                   qos=config.cfg.QOS)

        if not result:
            logging.error("Error publishing data to MQTT in send_data()")

        mqtt_communicator.disconnect()
        wireless_controller.disconnect_station()

    @staticmethod
    def print_time() -> None:
        time = utime.localtime()
        logging.debug(
            "Actual time: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(time[0], time[1], time[2], time[3], time[4],
                                                                        time[5]))

    @staticmethod
    def go_to_sleep(event: MainControllerEvent) -> None:
        """
        Go to deep sleep.
        """
        # Resets flag before sleep
        config.cfg.printed_time = False
        config.cfg.got_sensor_data = False
        config.cfg.published_to_cloud = False
        config.cfg.save()

        logging.debug("sleep({})".format(event.data))
        ms = int(event.data['ms'])
        if ms <= 0:
            ms = 10
        machine.deepsleep(ms)

    def start_test_data_acquisition_hook(self) -> None:
        pass

    def start_data_acquisition_hook(self) -> None:
        pass
