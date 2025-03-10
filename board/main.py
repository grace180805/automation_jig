# Complete project details at https://RandomNerdTutorials.com/micropython-programming-with-esp32-and-esp8266/
import json

from common.my_servo import MyServo
from common.wifi import WiFi
from common.config import configure
from common.my_mqtt import MyMQTT
from common.my_uart import MyUART
from common.enum_data import CalibrationEnum
from common.enum_data import MessageEnum
from common import logging

import time
import ubinascii
import machine
import esp
import gc
import _thread

esp.osdebug(None)
gc.collect()
uart = MyUART()


def get_logger():
    # Create logger
    logger = logging.getLogger('esp32')

    # Create console handler and set level to debug
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    # Create file handler and set level to error
    file_handler = logging.FileHandler("debug.log", mode="w")
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter("%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s")

    # Add formatter to the handlers
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def sub_cb(topic, msg):
    str_topic = topic.decode("utf-8")
    str_msg = msg.decode("utf-8")

    print('get message %s from topic %s' % (str_msg, str_topic))

    my_servo = MyServo()

    if (str_topic.find(CalibrationEnum.LOCK_OPEN) > -1
        or str_topic.find(CalibrationEnum.LOCK_CLOSE) > -1
        or str_topic.find(CalibrationEnum.LOCK_JUST_OPEN) > -1
        or str_topic.find(CalibrationEnum.LOCK_JUST_CLOSE) > -1
        or str_topic.find(CalibrationEnum.LOCK_FULLY_OPEN) > -1
        or str_topic.find(CalibrationEnum.LOCK_FULLY_CLOSE) > -1) and msg.find(MessageEnum.move) > -1:

        steps = str(msg).split("&")[1]
        step = steps.split('=')[1]
        step = step[:-1]
        inst = uart.get_instructions(step)
        #         time.sleep(2)
        uart.write(inst)

        time.sleep(2)
        #         if uart.is_return_cmd_success():
        #             mqtt_client.publish(topic, MessageEnum.success)

        uart.close_torque()
    elif str_topic.find(CalibrationEnum.DOOR_CLOSE) > -1 and msg.find(MessageEnum.move) > -1:
        my_servo.write_angle(0)
        time.sleep(1)
        mqtt_client.publish(topic, MessageEnum.success)
    elif str_topic.find(CalibrationEnum.DOOR_AJAR) > -1 and msg.find(MessageEnum.move) > -1:
        my_servo.write_angle(10)
        time.sleep(1)
        mqtt_client.publish(topic, MessageEnum.success)
    elif str_topic.find(CalibrationEnum.DOOR_OPEN) > -1 and msg.find(MessageEnum.move) > -1:
        my_servo.write_angle(45)
        time.sleep(1)
        mqtt_client.publish(topic, MessageEnum.success)

    elif (str_topic.find(CalibrationEnum.LOCK_FLIPUP) > -1) and msg.find(MessageEnum.move) > -1:
        uart.open_torque()

    elif (str_topic.find(CalibrationEnum.LOCK_FLIPDOWN) > -1) and msg.find(MessageEnum.move) > -1:
        uart.close_torque()


temp_location = 0


def get_location_and_publish():
    while True:
        global temp_location, uart
        if uart.is_servo_moving() is False:
            time.sleep(2)
            location = uart.get_current_steps()
            if temp_location != location and location is not None:
                temp_location = location
                mqtt_client.publish(configure["jig_id"] + '/' + CalibrationEnum.LOCK_STATUS, "steps=%s" % location)



def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()


if __name__ == '__main__':
    print('\r\nStart connect wifi')
    wifi = WiFi(ssid=configure["wifi_ssid"], password=configure["wifi_pwd"])
    wifi.connect()

    print('\r\nStart connect MQTT')
    client_id = ubinascii.hexlify(machine.unique_id())
    mqtt_server = configure["mqtt_server"]
    mqtt_user = configure["mqtt_user"]
    mqtt_pwd = configure["mqtt_pwd"]
    sub_topic = configure["sub_topic"]

    my_mqtt = MyMQTT(client_id=client_id, mqtt_server=mqtt_server, mqtt_user=mqtt_user, mqtt_pwd=mqtt_pwd)

    try:
        my_mqtt.connect_and_subscribe(callback_fun=sub_cb, topic=sub_topic)

    except OSError as e:
        restart_and_reconnect()

    mqtt_client = my_mqtt.client
    uart.close_torque()

    _thread.start_new_thread(get_location_and_publish, ())

    while True:
        try:
            mqtt_client.check_msg()
        except OSError as e:
            restart_and_reconnect()
