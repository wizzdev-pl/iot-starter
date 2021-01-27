class MainControllerStateName():
    IDLE = 0
    ACCESS_POINT = 1
    DATA_ACQUISITION_RUNNING = 2
    DATA_ACQUISITION_PAUSED = 3
    ERROR = 4


class MainControllerState():
    def __init__(self):
        self.state = MainControllerStateName.IDLE

    def is_idle(self):
        return self.state == MainControllerStateName.IDLE

    def is_access_point(self):
        return self.state == MainControllerStateName.ACCESS_POINT

    def is_data_acquisition_running(self):
        return self.state == MainControllerStateName.DATA_ACQUISITION_RUNNING

    def is_data_acquisition_paused(self):
        return self.state == MainControllerStateName.DATA_ACQUISITION_PAUSED

    def is_error(self):
        return self.state == MainControllerStateName.ERROR

    def set_idle(self):
        if self.state != MainControllerStateName.ERROR:
            # log error
            return False
        self.state = MainControllerStateName.IDLE
        return True

    def set_access_point(self):
        if self.state != MainControllerStateName.IDLE:
            # log error
            return False
        self.state = MainControllerStateName.ACCESS_POINT
        return True

    def set_data_acquisition_running(self):
        self.state = MainControllerStateName.DATA_ACQUISITION_RUNNING

    def set_data_acquisition_paused(self):
        self.state = MainControllerStateName.DATA_ACQUISITION_PAUSED

    def set_error(self):
        self.state = MainControllerStateName.ERROR
