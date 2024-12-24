# from datetime import datetime
import paho.mqtt.client as paho
from paho import mqtt
# import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

username = 'soilsensors'
password = 'LrrJ$DYofq7E~Qq4wiAM'
broker_url = '12cf26cf242b4a79a708f6d76358a44d.s1.eu.hivemq.cloud'
broker_port = 8883
sensor_id = 'soil001'
topic = 'soil'

unacked_publish = set()

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, rc, properties):
    print("mid: " + str(mid))

def send_data(client,topic,data):
    client.loop_start()
    # a single publish, this can also be done in loops, etc.
    msg_info = client.publish(topic, payload=str(data), qos=1)
    unacked_publish.add(msg_info.mid)

    msg_info.wait_for_publish()
    client.loop_stop()

def init_broker_client():
    try:
        # using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
        # userdata is user defined data of any type, updated by user_data_set()
        # client_id is the given name of the client
        broker_client = paho.Client(paho.CallbackAPIVersion.VERSION2)
        broker_client.on_connect = on_connect

        # enable TLS for secure connection
        broker_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        # Set username and password
        broker_client.username_pw_set(username, password)
        # connect to HiveMQ Cloud on port 8883 (default for MQTT)
        broker_client.connect(broker_url, broker_port)

        # setting callbacks, use separate functions like above for better visibility
        # broker_client.on_subscribe = on_subscribe
        # broker_client.on_message = on_message
        broker_client.on_publish = on_publish
        return broker_client
    except Exception as e:
        print('Error in MQTT initialization')
        print(e)

def disconnect(broker_client):
    try:
        broker_client.loop_stop()
        broker_client.disconnect()
        return True
    except Exception as e:
        print('Error in MQTT initialization')
        print(e)
        return False

# broker_client = init_broker_client()
# send_data(client=broker_client,topic=topic+'\data',data=data)
# disconnect(broker_client)

