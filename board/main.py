# Complete project details at https://RandomNerdTutorials.com/micropython-programming-with-esp32-and-esp8266/
import json

from common.my_servo import MyServo
from common.wifi import WiFi
from common.config import configure
from common.my_mqtt import MyMQTT
from common.my_uart import MyUART
from common.enum_data import CalibrationEnum
from common.enum_data import MessageEnum
from common.my_logging import get_logger

import time
import ntptime
import ubinascii
import machine
import esp
import gc
import _thread
import os
import sys

# install package
# import mip
# mip.install("logging")
# mip.install("time")

esp.osdebug(None)
gc.collect()
uart = MyUART()
my_servo = MyServo()

logger = get_logger()
return_location = True

random_num = int.from_bytes(os.urandom(3), 'little')
client_id = bytes('client_' + str(random_num), 'utf-8')
#     client_id = ubinascii.hexlify(machine.unique_id())
mqtt_server = configure["mqtt_server"]
mqtt_user = configure["mqtt_user"]
mqtt_pwd = configure["mqtt_pwd"]
sub_topic = configure["sub_topic"]
my_mqtt = MyMQTT(client_id=client_id, mqtt_server=mqtt_server, mqtt_user=mqtt_user, mqtt_pwd=mqtt_pwd)


def sub_cb(topic, msg):
    global return_location
    str_topic = topic.decode("utf-8")
    str_msg = msg.decode("utf-8")
    #     global my_servo
    #     print(my_servo)
    #
    #
    logger.info('get message %s from topic %s' % (str_msg, str_topic))

    if (str_topic.find(CalibrationEnum.LOCK_OPEN) > -1
        or str_topic.find(CalibrationEnum.LOCK_CLOSE) > -1
        or str_topic.find(CalibrationEnum.LOCK_JUST_OPEN) > -1
        or str_topic.find(CalibrationEnum.LOCK_JUST_CLOSE) > -1
        or str_topic.find(CalibrationEnum.LOCK_FULLY_OPEN) > -1
        or str_topic.find(CalibrationEnum.LOCK_FULLY_CLOSE) > -1) and msg.find(MessageEnum.move) > -1:

        return_location = False

        steps = str(msg).split("&")[1]
        step = steps.split('=')[1]
        step = step[:-1]
        inst = uart.get_instructions(step)
        uart.write(inst)

        time.sleep(5)
        #         if uart.is_return_cmd_success():
        #             mqtt_client.publish(topic, MessageEnum.success)

        uart.close_torque()
        time.sleep(0.1)
        return_location = True
    elif str_topic.find(CalibrationEnum.DOOR_CLOSE) > -1 and msg.find(MessageEnum.move) > -1:
        my_servo.write_angle(0)
        time.sleep(0.1)
        mqtt_client.publish(topic, MessageEnum.success)
    elif str_topic.find(CalibrationEnum.DOOR_AJAR) > -1 and msg.find(MessageEnum.move) > -1:
        my_servo.write_angle(10)
        time.sleep(0.1)
        mqtt_client.publish(topic, MessageEnum.success)
    elif str_topic.find(CalibrationEnum.DOOR_OPEN) > -1 and msg.find(MessageEnum.move) > -1:
        #         print('in door open')
        my_servo.write_angle(45)
        time.sleep(0.1)
        mqtt_client.publish(topic, MessageEnum.success)

    elif (str_topic.find(CalibrationEnum.LOCK_FLIPUP) > -1) and msg.find(MessageEnum.move) > -1:
        uart.open_torque()

    elif (str_topic.find(CalibrationEnum.LOCK_FLIPDOWN) > -1) and msg.find(MessageEnum.move) > -1:
        uart.close_torque()


temp_location = 0


#
# def set_angle(angle):
#     global my_servo
#     try:
#         my_servo.write_angle(angle)
#     except KeyboardInterrupt:
#         my_servo.pwm.deinit()  # 停止 PWM
#
# def get_location_and_publish():
#     global temp_location, uart
#     if uart.is_servo_moving() is False:
#         time.sleep(2)
#         location = uart.get_current_steps()
#         if location is not None:
#             mqtt_client.publish(configure["jig_id"]+'/'+CalibrationEnum.LOCK_STATUS, "steps=%s" % location)
#             time.sleep(1)


def get_location_and_publish():
    while True:
        global temp_location, return_location
        if return_location:
            #             if uart.is_servo_moving() is False:
            time.sleep(1)
            location = uart.get_current_steps()
            if temp_location != location and location is not None:
                temp_location = location
                mqtt_client.publish(configure["jig_id"] + '/' + CalibrationEnum.LOCK_STATUS, "steps=%s" % location)


def restart_and_reconnect():
    logger.info('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(1)
    machine.reset()


def set_time():
    ntptime.settime()  # 默认使用 "pool.ntp.org" 作为 NTP 服务器


#     print("同步后本地时间：", time.localtime())
#     # 设置时区为东八区
#     UTC_OFFSET = 8 * 3600  # 东八区
#     localtime_now = time.localtime(time.time() + UTC_OFFSET)
#     print("调整后本地时间：", localtime_now)
#

def connect_and_subscribe_mqtt():
    is_connected = False
    if not wifi.connect():
        print("WiFi 连接失败，无法建立 MQTT 连接")
    for attempt in range(3):
        if is_connected is False:
            if attempt == 2:
                print('Failed to connect to MQTT broker. restart...')
                machine.reset()
            try:
                my_mqtt.connect_and_subscribe(callback_fun=sub_cb, topic=sub_topic)
                is_connected = True
            except OSError as e:
                if e.args[0] == 116:  # ETIMEDOUT
                    print('%s - 连接超时' % e)
                elif e.args[0] == 113:  # EHOSTUNREACH
                    print('%s - 主机不可达' % e)
                elif e.args[0] == 118:  # EADDRNOTAVAIL
                    print('%s - 地址不可用' % e)
                else:
                    print(e)
                try:
                    if my_mqtt:
                        my_mqtt.disconnect()
                except:
                    pass
            except Exception as e:
                try:
                    if my_mqtt:
                        my_mqtt.disconnect()
                except:
                    pass


if __name__ == '__main__':
    try:
        logger.info('Start connect wifi')
        wifi = WiFi(ssid=configure["wifi_ssid"], password=configure["wifi_pwd"])
        wifi.connect()

        #         set_time()

        #         logger.info('Start connect MQTT')
        try:
            connect_and_subscribe_mqtt()
        #             my_mqtt.connect_and_subscribe(callback_fun = sub_cb, topic = sub_topic)

        except Exception as e:
            logger.info('Could not connect to MQTT Server')
            machine.reset()

        mqtt_client = my_mqtt.client
        uart.close_torque()
        try:
            _thread.start_new_thread(get_location_and_publish, ())
        except Exception as e:
            connect_and_subscribe_mqtt()
        #             my_mqtt.connect_and_subscribe(callback_fun = sub_cb, topic = sub_topic)

        while True:
            try:
                if not wifi.station.isconnected():
                    wifi.connect()
                mqtt_client.check_msg()
            except Exception as e:
                connect_and_subscribe_mqtt()
    #                 my_mqtt.connect_and_subscribe(callback_fun = sub_cb, topic = sub_topic)
    except Exception as e:
        logger.info('error')
        logger.info(e)
        machine.reset()





