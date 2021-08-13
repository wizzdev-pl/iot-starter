class Providers:
    AWS = "AWS"
    KAA = "KAA"
    THINGSBOARD = "THINGSBOARD"


class CloudProvider:
    def device_configuration(self):
        pass

    def publish_data(self, data):
        """
        Publish data to the cloud
        :param data: data to be sent to cloud
        :return: None
        """
        pass

    def check_connection(self):
        pass