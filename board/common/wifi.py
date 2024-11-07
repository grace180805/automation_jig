import network

class WiFi:
    
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
    
    def connect(self):
        station = network.WLAN(network.STA_IF)
        station.active(True)
        station.connect(self.ssid, self.password)
        while station.isconnected() == False:
          pass
        print(station.ifconfig())
        print('Connection successful')
        

