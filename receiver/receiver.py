import paho.mqtt.client as mqtt
from base64 import b64decode
from datetime import datetime
import os
mqtt_broker_address = hostname
mqtt_port = 1883

from config import username, hostname, password


def on_connect(client, userdata, rc):
    print('Connected with result code '+str(rc))
    client.subscribe('comp/#')


def on_message(client, userdata, msg):
    print "Topic: ", msg.topic
    topic = str(msg.topic)+'/'
    if not os.path.exists(os.path.dirname(topic)):
        try:
            os.makedirs(os.path.dirname(topic))
        except:
            pass
    if 'text' in topic:
        data = str(msg.payload)
        with open(topic+"/log.txt", "a+") as f:
            f.write(data)
    if 'webcam' in topic:
        data = b64decode(msg.payload)
        with open(topic+'/'+str(datetime.now()).replace(':', '-')[:-7]+".jpg", 'wb+') as f:
            f.write(data)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username, password)
client.connect(mqtt_broker_address, mqtt_port, 60)

client.loop_forever()

