import wiotp.sdk.device
import time
import os
import datetime
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import playsound

authenticator = IAMAuthenticator('xP-FJmnJUbVYZG3C_zFINVfxmPNkQ1jtQnPcbnDLvUBi')
text_to_speech = TextToSpeechV1(
    authenticator=authenticator
)

text_to_speech.set_service_url('https://api.eu-gb.text-to-speech.watson.cloud.ibm.com/instances/277349e4-c7cb-4f5e-bb0c-6f437492ba33')

myConfig = { 
    "identity": {
        "orgId": "hj5fmy",
        "typeId": "Device1",
        "deviceId": "67890"
    },
    "auth": {
        "token": "87654321"
    }
}
client = wiotp.sdk.device.DeviceClient(config=myConfig, logHandlers=None)
client.connect()


def myCommandCallback(cmd):
    print("Message received from IBM IoT Platform: %s" % cmd.data['command'])
    m=cmd.data['command']
    if(m=="lighton"):
        print("Light is switched on")
    elif(m=="lightoff"):
         print("Light is switched OFF")
while True:
    #myData={'Face_detection': detect}
    #client.publishEvent(eventId="status", msgFormat="json", data=myData, qos=0, onPublish=None)
    client.commandCallback = myCommandCallback
client.disconnect()

with open('hello_world.mp3', 'wb') as audio_file:
        audio_file.write(
            text_to_speech.synthesize(
                'You have to take '+m+' medicine now',
                voice='en-US_AllisonV3Voice',
                accept='audio/mp3'        
            ).get_result().content)
playsound.playsound('hello_world.mp3')
os.remove('hello_world.mp3')
    

