import time

import network
from machine import Pin, unique_id, ADC


class WiFi:
    station = network.WLAN(network.STA_IF)
    wifi_led = Pin(2, Pin.OUT)

    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password

    def connect(self):
        self.station.active(True)
        self.station.connect(self.ssid, self.password)
        while self.station.isconnected() == False:
            pass
        self.wifi_led.value(1)
        print(self.station.ifconfig())
        print('Connection wifi successful')

    # def check_wifi_state(self):
    #     while True:
    #         time.sleep(5)
    #         if self.station.isconnected():
    #             self.wifi_led.value(0)
    #             print('Re-Connection wifi:')
    #             self.connect()
