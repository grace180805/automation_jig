import ssl

from flask import Flask, request, jsonify
from flask_mqtt import Mqtt

from api.src import config

app = Flask(__name__)

# method 1
# app.config['MQTT_BROKER_URL'] = config.configure["mqtt_host"]
# app.config['MQTT_BROKER_PORT'] = 8883
# app.config['MQTT_CLIENT_ID'] = 'server'
# app.config['MQTT_TLS_VERSION'] = ssl.PROTOCOL_TLS
# app.config['MQTT_USERNAME'] = config.configure["mqtt_user"]  # Set this item when you need to verify username and password
# app.config['MQTT_PASSWORD'] = config.configure["mqtt_pwd"]  # Set this item when you need to verify username and password
# # app.config['MQTT_KEEPALIVE'] = 60  # Set KeepAlive time in seconds
# app.config['MQTT_TLS_ENABLED'] = True  # If your broker supports TLS, set it True


# method 2
app.config['MQTT_BROKER_URL'] = config.configure["mqtt_host"]  # URL for HiveMQ cluster
app.config['MQTT_USERNAME'] = config.configure["mqtt_user"]  # From the credentials created in HiveMQ
app.config['MQTT_PASSWORD'] = config.configure["mqtt_pwd"]  # From the credentials created in HiveMQ
app.config['MQTT_CLIENT_ID'] = 'test'  # Must be unique for any client that connects to the cluster
app.config['MQTT_BROKER_PORT'] = 8883  # MQTT port for encrypted traffic
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = True
app.config['MQTT_TLS_INSECURE'] = False
app.config['MQTT_TLS_CA_CERTS'] = 'MQTT/isrgrootx1.pem'  # CA for HiveMQ, read: https://letsencrypt.org/about/
app.config['MQTT_TLS_VERSION'] = ssl.PROTOCOL_TLSv1_2
app.config['MQTT_TLS_CIPHERS'] = None

topic = '#'

mqtt_client = Mqtt(app)


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(topic) # subscribe topic
   else:
       print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
   data = dict(
       topic=message.topic,
       payload=message.payload.decode()
  )
   print('Received message on topic: {topic} with payload: {payload}'.format(**data))


@app.route('/send', methods=['POST'])
def publish_message():
    request_data = request.get_json()
    jig_id = request_data["jigID"]
    topic = request_data["topic"]
    device_type = request_data["deviceType"]
    new_topic = '/automation/{}/{}/{}'.format(device_type, jig_id, topic)
    publish_result = mqtt_client.publish(new_topic, topic, qos=2)
    return jsonify({'code': publish_result[0]})


if __name__ == '__main__':
   app.run(host='127.0.0.1', port=5000)
