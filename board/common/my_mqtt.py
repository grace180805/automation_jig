from board.common.umqttsimple import MQTTClient


class MyMQTT:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(MyMQTT, cls).__new__(cls)
        return cls._instance

    def __init__(self, client_id, mqtt_server, mqtt_user, mqtt_pwd):
        self.client = MQTTClient(client_id, mqtt_server, user=mqtt_user, password=mqtt_pwd, ssl=True,
                                 ssl_params={"server_hostname": mqtt_server})

    def connect_and_subscribe(self, callback_fun, topic):
        self.client.set_callback(callback_fun)
        self.client.connect()
        self.client.subscribe(topic)
        print('Connected to MQTT broker, subscribed to %s topic' % (topic))

    def disconnect(self):
        self.client.disconnect()


