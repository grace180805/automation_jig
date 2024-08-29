# Complete project details at https://RandomNerdTutorials.com/micropython-programming-with-esp32-and-esp8266/

def sub_cb(topic, msg):
  print((topic, msg))
#   if topic == b'notification' and msg == b'received':
#     print('ESP received hello message')
  if msg == b'lock':      
    motor=Servo(pin=13) # A changer selon la broche utilisée
    motor.move(0) # tourne le servo à 0°
    time.sleep(0.3)
    motor.move(90) # tourne le servo à 90°
    time.sleep(0.3)

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server, user=mqtt_user, password=mqtt_pass,ssl=True, ssl_params={"server_hostname" : mqtt_server})
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
#     if (time.time() - last_message) > message_interval:
#       msg = b'Hello #%d' % counter
#       client.publish(topic_pub, msg)
#       last_message = time.time()
#       counter += 1
  except OSError as e:
    restart_and_reconnect()