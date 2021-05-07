class Providers:
    AWS = "AWS"
    KAA = "KAA"


class CloudProvider:
    def device_configuration(self):
        pass

    def publish_data(self):
        """
        Publish data to the cloud
        :return: None
        """
        pass

    def check_connection(self):
        pass