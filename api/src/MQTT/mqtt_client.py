import paho.mqtt.client as paho
from paho import mqtt

from src import config


class MQTTClient:
    client = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(MQTTClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # self.username = username
        # self.password = password
        client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        client.username_pw_set(config.configure["mqtt_user"], config.configure["mqtt_pwd"])
        client.connect(config.configure["mqtt_host"], 8883)
        self.client = client
        self.client.on_message = self.on_message
        self.client.on_publish =self.on_publish
        self.client.on_subscribe = self.on_subscribe

    def on_publish(client, userdata, mid, properties=None):
        """
            Prints mid to stdout to reassure a successful publish ( used as callback for publish )

            :param client: the client itself
            :param userdata: userdata is set when initiating the client, here it is userdata=None
            :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
            :param properties: can be used in MQTTv5, but is optional
        """
        print("mid: " + str(mid))

    # print which topic was subscribed to
    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        """
            Prints a reassurance for successfully subscribing

            :param client: the client itself
            :param userdata: userdata is set when initiating the client, here it is userdata=None
            :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
            :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
            :param properties: can be used in MQTTv5, but is optional
        """
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    # print message, useful for checking if it was successful
    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
