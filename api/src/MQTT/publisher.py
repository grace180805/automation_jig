import paho.mqtt.client as paho
from paho import mqtt

from src import config


class MQTTPublisher:
    publisher_client = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(MQTTPublisher, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # self.username = username
        # self.password = password
        client = paho.Client(client_id="api_publisher", userdata=None, protocol=paho.MQTTv5)
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        client.username_pw_set(config.configure["mqtt_user"], config.configure["mqtt_pwd"])
        client.connect(config.configure["mqtt_host"], 8883)
        self.publisher_client = client
        self.publisher_client.on_message = self.on_message
        self.publisher_client.on_publish = self.on_publish


    def on_publish(client, userdata, mid, properties=None):
        """
            Prints mid to stdout to reassure a successful publish ( used as callback for publish )

            :param client: the client itself
            :param userdata: userdata is set when initiating the client, here it is userdata=None
            :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
            :param properties: can be used in MQTTv5, but is optional
        """
        print("client: {} mid:{} ".format(str(client), str(mid)))

    # print message, useful for checking if it was successful
    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))