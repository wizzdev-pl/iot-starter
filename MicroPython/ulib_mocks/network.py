STA_IF = 0
AP_IF = ...

class WLAN:


    def __init__(self, mode):
        self.activeated = False
        self.connected = False
        pass

    def active(self, active:bool):
        self.activeated = active
        return self.activeated

    def isconnected(self):
        return self.connected

    def connect(self, ssid, pwd):
        import time
        time.sleep(3)
        self.connected = True

    def disconnect(self):
        self.connected = False

    def ifconfig(self):
        return "0.0.0.0, 0.0.0.0, 0.0.0.0"

    def config(self, essid, password):
        pass

