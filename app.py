#### Leverages the AWS IoT SDK for Python

# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import settings  # importing configuration file
import device  # import device class
import time
import random
import string


# set up the gps coords variables
def random_GPS():
    """Returns a random Latitude/Longitude pair roughly located in the Continental US"""
    lat = random.uniform(30, 50)
    lon = random.uniform(-77, -122)
    coor = (lat,lon)
    return coor

def random_light():
    return random.randint(0,1000)

def random_audio():
    return random.randint(0,100)

# create devices
dev_names = ['Hitesh','Richa','Saumya']
dev_id = ['arn:aws:sns:us-east-1:582363083840:IOTTopic:165c159a-f916-4bf3-8f69-e78c31521d57','arn:aws:sns:us-east-1:582363083840:IOTTopic:831d47a0-e23b-4ac5-a917-0629069098e9','arn:aws:sns:us-east-1:582363083840:IOTTopic:976e10bc-0666-42d5-9c8c-c2c2257463fe']
devs = []  # set up a list to hold your devices
for i in range(len(dev_names)):
    coor = random_GPS()
    devs.append(device.Device(dev_names[i], coor[0], coor[1],random_light(),random_audio(),dev_id[i]))
RECHARGE_ALERT_TOPIC = "device/+/rechargeAlert"  # subscribe to wildcard device_id

# Create a random 8-character string for connection id
CLIENT_ID = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))

def on_message(client, userdata, msg):
    # CURRENT_COLOR = new_color()
    # print(CURRENT_COLOR+"ALERT: Received message on topic "+msg.topic+" with payload: "+str(msg.payload))
    # print("ALERT: Received message on topic "+msg.topic+" with payload: "+str(msg.payload))
    name =  msg.topic.split('/')[1]
    print("ALERT: Received message on topic "+msg.topic+" to recharge device: " + name)
    # loop through device list to recharge the correct device
    for x in devs:
        if x.name == msg.topic.split('/')[1]:
            x.recharge_device_battery()

# create AWS IoT MQTT client
client = AWSIoTMQTTClient(CLIENT_ID)

# configure client endpoint / port information & then set up certs
client.configureEndpoint(settings.HOST_NAME, settings.HOST_PORT)
client.configureCredentials(settings.ROOT_CERT, settings.PRIVATE_KEY, settings.DEVICE_CERT)

# configure client connection behavior
client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
client.configureDrainingFrequency(2)  # Draining: 2 Hz
client.configureConnectDisconnectTimeout(10)  # 10 sec
client.configureMQTTOperationTimeout(5)  # 5 sec

print("Connecting to endpoint " + settings.HOST_NAME)
client.connect()
print("Subscribing to " + RECHARGE_ALERT_TOPIC)
client.subscribe(RECHARGE_ALERT_TOPIC, 1, on_message)

# start loop to begin publishing to topic
while True:

    for dev in devs:
        client.publish("device/" + dev.name + "/devicePayload", dev.get_payload(), settings.QOS_LEVEL)
        print("Published message on topic " + "device/" + dev.name + "/devicePayload" + " with payload: " + dev.get_payload())
        dev.update() # update the device with new data
    time.sleep(30) # just wait a sec before publishing next message
