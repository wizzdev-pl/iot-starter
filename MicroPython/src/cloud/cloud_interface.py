class Providers:
    AWS = "AWS"
    KAA = "KAA"


class CloudProvider:
    def __init__(self) -> None:
        pass

    def device_configuration(self):
        pass

    def send_data(self):
        pass

    def check_connection(self):
        pass