import wiotp.sdk.device
import time
import os
import datetime
import random
myConfig = { 
    "identity": {
        "orgId": "hj5fmy",
        "typeId": "NodeMCU",
        "deviceId":"12345"
    },
    "auth": {
        "token": "12345678"
    }
}

def myCommandCallback(cmd):
    print("Message received from IBM IoT Platform: %s" % cmd.data['command'])
    m=cmd.data['command']
    if(m=="lighton"):
        print("Light is switched ON")
    elif(m=="lightoff"):
         print("Light is switched OFF")
    elif(m=="fanon"):
         print("Fan is switched ON")
    elif(m=="fanoff"):
         print("Fan is switched OFF")
    print(" ")
client = wiotp.sdk.device.DeviceClient(config=myConfig, logHandlers=None)
client.connect()

while True:
    temp=random.randint(-20,125)
    hum=random.randint(0,100)
    myData={'temperature':temp, 'humidity':hum}
    client.publishEvent(eventId="status", msgFormat="json", data=myData, qos=0, onPublish=None)
    print("Published data Successfully: %s", myData)
    client.commandCallback = myCommandCallback
    time.sleep(2)
client.disconnect()
