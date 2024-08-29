from flask import Flask, request, jsonify

from src import config
from src.MQTT.mqtt_client import MQTTClient
from src.MQTT.publisher import MQTTPublisher
from src.MQTT.subscriber import MQTTSubscriber

app = Flask(__name__)

publisher = MQTTPublisher().publisher_client
subscriber = MQTTSubscriber()
# client.client.loop_forever()


@app.route('/send', methods=['POST'])
def hello():
    jig_id = request.form.get("jigID")
    topic = request.form.get("topic")
    device_type = request.form.get("deviceType")
    topic = '/automation/{}/{}/{}'.format(device_type, jig_id, topic)
    print(topic)
    publisher.publish(topic=topic, payload='topic', qos=2)
    return jsonify({'status': 'ok'})

@app.route('/receive/<topic>', methods=['GET'])
def receive(topic):
    # client.subscribe(topic=topic, qos=2)
    # client.
    return jsonify({'status': 'ok'})



if __name__ == '__main__':
    app.run()