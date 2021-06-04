class MainControllerEventType:
    CONFIGURE_ACCESS_POINT = 0
    TEST_CONNECTION = 3
    PRINT_TIME = 4
    GET_SENSOR_DATA = 5
    PUBLISH_DATA = 6
    GO_TO_SLEEP = 7
    ERROR_OCCURRED = 99


class MainControllerEvent:
    def __init__(self, event_type: MainControllerEventType, callback=None, **data):
        self.event_type = event_type
        self.callback = callback
        self.data = data
