import paho.mqtt.client as paho
from paho import mqtt
from src import config


class MQTTSubscriber:
    subscriber_client = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(MQTTSubscriber, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # self.username = username
        # self.password = password
        client = paho.Client(client_id="api_subscriber", userdata=None, protocol=paho.MQTTv5)
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        client.username_pw_set(config.configure["mqtt_user"], config.configure["mqtt_pwd"])
        client.connect(config.configure["mqtt_host"], 8883)
        self.subscriber_client = client
        self.subscriber_client.on_message = self.on_message
        self.subscriber_client.loop_forever()

    # print message, useful for checking if it was successful
    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))