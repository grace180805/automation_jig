# Complete project details at https://RandomNerdTutorials.com/micropython-programming-with-esp32-and-esp8266/
from common.wifi import WiFi
from common.config import configure, MAX_RETRIES
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

esp.osdebug(None)
gc.collect()

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


def retrieve(func, *args):
    retry_count = 0
    while retry_count < MAX_RETRIES:
        result = func(*args)
        result_value=COMM_RX_FAIL
        error=0
        if len(result) == 2:
            result_value, error = result
        elif len(result) == 3:
            data, result_value, error = result
        if result_value == COMM_SUCCESS:
            if error != 0:
                print("test: ",error)
                utils.info("%s" % sts_servo.getRxPacketError(error))
            else:
                return data if len(result) == 3 else None
        else:
            retry_count += 1

def sub_cb(topic, msg):
    str_topic = topic.decode("utf-8")
    str_msg = msg.decode("utf-8")
   
    print('get message %s from topic %s' % (str_msg, str_topic))


    uart = MyUART()  
    my_servo = MyServo()

    if (str_topic.find(CalibrationEnum.LOCK_OPEN)>-1
        or str_topic.find(CalibrationEnum.LOCK_CLOSE)>-1
        or str_topic.find(CalibrationEnum.LOCK_JUST_OPEN)>-1
        or str_topic.find(CalibrationEnum.LOCK_JUST_CLOSE)>-1
        or str_topic.find(CalibrationEnum.LOCK_FULLY_OPEN)>-1
        or str_topic.find(CalibrationEnum.LOCK_FULLY_CLOSE)>-1) and msg.find(MessageEnum.move)>-1:
        
        
        steps = str(msg).split("&")[1]
        step = steps.split('=')[1]
        step = step[:-1]
        inst = uart.get_instructions(step)
        uart.clear_data()
        time.sleep(2)
        uart.write(inst)
        
#         uart.write(CalibrationEnum.cmd[str_topic[6:]])
        time.sleep(2)
        if uart.is_return_cmd_success():
            mqtt_client.publish(topic, MessageEnum.success)

        uart.clear_data()
    elif str_topic.find(CalibrationEnum.DOOR_CLOSE)>-1 and msg.find(MessageEnum.move)>-1:
        my_servo.write_angle(45)
    elif str_topic.find(CalibrationEnum.DOOR_AJAR)>-1 and msg.find(MessageEnum.move)>-1:
        my_servo.write_angle(35)
    elif str_topic.find(CalibrationEnum.DOOR_OPEN)>-1 and msg.find(MessageEnum.move)>-1:
        my_servo.write_angle(5)



    if (str_topic.find(CalibrationEnum.LOCK_FLIPUP) > -1) and msg.find(MessageEnum.move) > -1:
        retrieve(sts_servo.controlTorque, 1, TurnOnTorque)
        servoStatus = 1
        needIntervent = False
        pos, _, _ = sts_servo.readPosition()
        msg = {"lockState": checkLockStatus(pos), "mac": mac_str, "lastTopic": command}
        client.publish(topic='lock/status', msg=json.dumps(msg), qos=2)

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

    # current_position = uart.read_servo_position()  # 读取当前角度
    # if current_position is not None:
    #     uart.enable_torque(True)  # 启用扭矩保持
    #     print(f"Torque Enabled! Servo holding position at {current_position}.")
    # else:
    #     print("Failed to read servo position!")

    my_mqtt= MyMQTT(client_id = client_id, mqtt_server = mqtt_server,mqtt_user=mqtt_user, mqtt_pwd = mqtt_pwd)
    
    try:
        my_mqtt.connect_and_subscribe(callback_fun = sub_cb, topic = sub_topic)

    except OSError as e:
        restart_and_reconnect()


    mqtt_client = my_mqtt.client
        
    while True:
        try:
            mqtt_client.check_msg()
        except OSError as e:
            restart_and_reconnect()
