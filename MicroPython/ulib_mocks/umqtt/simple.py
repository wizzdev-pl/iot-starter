
class MQTTClient:
    def __init__(self, client_id, server, port=0, user=None, password=None, keepalive=0,
                 ssl=False, ssl_params={}):
        self.server = server
        self.port = port

    def _send_str(self, s):
        pass

    def _recv_len(self):
        pass

    def set_callback(self, f):
        pass

    def set_last_will(self, topic, msg, retain=False, qos=0):
        pass

    def connect(self, clean_session=True):
        pass

    def disconnect(self):
        pass

    def ping(self):
        pass

    def publish(self, topic, msg, retain=False, qos=0):
        pass

    def subscribe(self, topic, qos=0):
        pass

    def wait_msg(self):
        pass

    def check_msg(self):
        pass
