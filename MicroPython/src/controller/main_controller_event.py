class MainControllerEventType:
    CONFIGURE_ACCESS_POINT = 0
    START_DATA_ACQUISITION = 1
    START_TEST_DATA_ACQUISITION = 2
    ERROR_OCCURRED = 99


class MainControllerEvent:
    def __init__(self, event_type: MainControllerEventType, callback=None, **data):
        self.event_type = event_type
        self.callback = callback
        self.data = data
