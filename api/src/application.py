import ssl

from flask import request, jsonify
from flask_mqtt import Mqtt

import config
from database import Jig, LockAndDoorSteps
from api_enum_data import OperationEnum, LockAndDoorStatus, Message

import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

app = Flask(__name__)

if not app.debug:
    handler = RotatingFileHandler('api_server.log', maxBytes=10000, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

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
app.config['MQTT_LAST_WILL_QOS'] = 2

topic = '#'
mqtt_client = Mqtt(app)

# received_messages = []


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        # print('Connected successfully')
        mqtt_client.subscribe(topic)  # subscribe topic
    else:
        print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )

    # received_messages.append(data['payload'])
    if Message.SUCCESS.value in str(message.payload):
        record = Jig.get(Jig.jig_id == message.topic[:5])
        if (OperationEnum.LOCK_FULLY_OPEN.value in message.topic) \
                or (OperationEnum.LOCK_OPEN.value in message.topic) \
                or (OperationEnum.LOCK_JUST_OPEN.value in message.topic):
            record.lock_state = LockAndDoorStatus.LOCK_UNLOCK.value

        elif (OperationEnum.LOCK_FULLY_CLOSE.value in message.topic) \
                or (OperationEnum.LOCK_CLOSE.value in message.topic) \
                or (OperationEnum.LOCK_JUST_CLOSE.value in message.topic):
            record.lock_state = LockAndDoorStatus.LOCK_LOCK.value

        elif OperationEnum.DOOR_OPEN.value in message.topic:
            record.door_state = LockAndDoorStatus.DOOR_OPEN.value
        elif OperationEnum.DOOR_AJAR.value in message.topic:
            record.door_state = LockAndDoorStatus.DOOR_AJAR.value
        elif OperationEnum.DOOR_CLOSE.value in message.topic:
            record.door_state = LockAndDoorStatus.DOOR_CLOSED.value

        record.save()

    if data['topic'].find(OperationEnum.LOCK_STATUS.value) > -1 and data['payload'].find('steps') > -1:
        msg = data['payload']
        steps = int(msg.split('=')[1])
        jig_status_record = Jig.get(Jig.jig_id == message.topic[:5])
        lock_and_door_steps_record = LockAndDoorSteps.get(LockAndDoorSteps.model == jig_status_record.model)
        if steps <= lock_and_door_steps_record.lock_just_lock_steps+10:
            jig_status_record.lock_state = LockAndDoorStatus.LOCK_LOCK.value

        if lock_and_door_steps_record.lock_just_unlock_steps-10 <= steps:
            jig_status_record.lock_state = LockAndDoorStatus.LOCK_UNLOCK.value
        jig_status_record.save()
    print('Received message on topic: {topic} with payload: {payload}'.format(**data))


@app.route('/send', methods=['POST'])
def publish_message():
    request_data = request.get_json()
    jig_id = request_data["jigId"]
    print(jig_id)
    device_type = request_data["deviceType"]
    topic = request_data["topic"]
    new_topic = '/automation/{}/{}/{}'.format(jig_id, device_type, topic)
    publish_result = mqtt_client.publish(new_topic, topic, qos=2)
    return jsonify({'code': publish_result[0]})


@app.route('/jigModel', methods=['PUT'])
def jig_model_api():
    request_data = request.get_json()
    jig_id = request_data["jigId"]
    jig_model = request_data["model"]
    jig_model_options = ["forma_scan01", "forma_scan02"]
    if jig_model not in jig_model_options:
        return jsonify({'code': 10400, 'message': 'the jig model is not existed!'})
    new_topic = '{}/{}'.format(jig_id, OperationEnum.DOOR_CLOSE.value)
    publish_result = mqtt_client.publish(new_topic, Message.MOVE.value, qos=2)
    app.logger.info("publish init jig topic")
    record = Jig.get(Jig.jig_id == jig_id)
    # update
    record.model = jig_model
    record.save()
    # return jsonify({'code': publish_result[0]})
    return jsonify({'code': 200, 'message': 'success'})


# def get_angel(topic):
#     return {
#         'door/close': '1',
#         'door/ajar': '2',
#         'door/open': '3'
#     }.get(topic, 'error')
# 'error' is default value, can set by yourself

@app.route('/sendTopic', methods=['POST'])
def send_topic_api():
    request_data = request.get_json()
    jig_id = request_data["jigId"]
    device_type = request_data["deviceType"]
    topic = request_data["topic"]
    model = Jig.select().where(Jig.jig_id == jig_id).get().model
    model_steps_row = LockAndDoorSteps.get(LockAndDoorSteps.model == model)
    steps = 0

    if topic == OperationEnum.LOCK_FULLY_OPEN.value:
        steps = model_steps_row.lock_fully_unlock_steps
    elif topic == OperationEnum.LOCK_OPEN.value:
        steps = model_steps_row.lock_unlock_steps
    elif topic == OperationEnum.LOCK_JUST_OPEN.value:
        steps = model_steps_row.lock_just_unlock_steps

    elif topic == OperationEnum.LOCK_FULLY_CLOSE.value:
        steps = model_steps_row.lock_fully_lock_steps
    elif topic == OperationEnum.LOCK_CLOSE.value:
        steps = model_steps_row.lock_lock_steps
    elif topic == OperationEnum.LOCK_JUST_CLOSE.value:
        steps = model_steps_row.lock_just_lock_steps

    elif topic == OperationEnum.DOOR_OPEN.value:
        steps = model_steps_row.door_open_steps
    elif topic == OperationEnum.DOOR_AJAR.value:
        steps = model_steps_row.door_ajar_steps
    elif topic == OperationEnum.DOOR_CLOSE.value:
        steps = model_steps_row.door_closed_steps

    new_topic = '{}/{}'.format(jig_id, topic)
    if topic != OperationEnum.LOCK_STATUS.value:
        publish_result = mqtt_client.publish(new_topic, Message.MOVE.value+'&steps='+str(steps), qos=2)
    else:
        publish_result = mqtt_client.publish(new_topic, qos=2)

    # if not received_messages:
    #     return jsonify({"message": "No messages received"}), 404
    # latest_message = received_messages.pop(0)
    return jsonify({'code': 200, 'message': 'success'})
    # else:
    #     return jsonify({'code': 500, 'message': 'operate jig failed'})


@app.route('/lockAndDoorStatus/<jig_id>', methods=['GET'])
def status_api(jig_id):
    query = Jig.select().where(Jig.jig_id == jig_id)
    result = query.get()
    data = {'doorState': result.door_state,
            'lockState': result.lock_state,
            "jigState": result.jig_state,
            'model': result.model}
    return jsonify({'code': 200, 'data': data, 'message': 'success'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
