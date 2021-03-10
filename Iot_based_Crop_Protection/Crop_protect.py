import json
from watson_developer_cloud import VisualRecognitionV3
import cv2
import wiotp.sdk.device
import time
import random
import datetime
import ibm_boto3
import requests
from ibm_botocore.client import Config, ClientError
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

COS_ENDPOINT = "https://s3.jp-tok.cloud-object-storage.appdomain.cloud" # Current list avaiable at https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
COS_API_KEY_ID = "f6Ap-ct18mO7S9UzL7XPbAF7l70omePLLUQOzqmnAzb5" # eg "W00YiRnLW4a3fTjMB-odB-2ySfTrFBIQQWanc--P3byk"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/6b644a3fda97448b888c23eeef263ed6:199ab1e5-0d9d-420f-8e4a-98d868c04368::" # eg "crn:v1:bluemix:public:cloud-object-storage:global:a/3bf0d9003abfb5d29761c3e97696b71c:d6f04d83-6c4f-4a62-a165-696756d63903::"

clientdb = Cloudant("apikey-v2-16u3crmdpkghhxefdikvpssoh5fwezrmuup5fv5g3ubz", "b0ab119f45d3e6255eabb978e7e2f0e1", url="https://apikey-v2-16u3crmdpkghhxefdikvpssoh5fwezrmuup5fv5g3ubz:b0ab119f45d3e6255eabb978e7e2f0e1@4da1d4e4-ad43-44c2-ab4f-510850d2529e-bluemix.cloudantnosqldb.appdomain.cloud")
clientdb.connect()

cam=cv2.VideoCapture('Horse.mp4')
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))


def vis(image):
	visual_recognition = VisualRecognitionV3(
	    '2018-03-19',
	    iam_apikey='4iHUKBMoK4OTebxnZLrHOmfOHU2MRG5Im_b-OGUMuPMQ')

	with open('./'+image, 'rb') as images_file:
	    classes = visual_recognition.classify(
		images_file,
		threshold='0.6',
		classifier_ids='default').get_result()
	#print(classes)
	a=classes["images"][0]["classifiers"][0]["classes"]
	for i in a:
		#print(i["class"])
		if i["class"]=="animal":
			print("Animal Detected")
			return "animal"

def myCommandCallback(cmd):
    print("Command received: %s" % cmd.data)


myConfig = { 
    "identity": {
        "orgId": "hj5fmy",
        "typeId": "NodeMCU",
        "deviceId": "12345"
    },
    "auth": {
        "token": "12345678"
    }
}
client = wiotp.sdk.device.DeviceClient(config=myConfig, logHandlers=None)
client.connect()

database_name = "sample"
my_database = clientdb.create_database(database_name)
if my_database.exists():
   print("'{database_name}' successfully created.")

while True:
	ret, frame=cam.read()
	gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	frame=cv2.resize(frame,(600,400))
	cv2.imwrite("image.jpg",frame)
	a=vis("image.jpg")
	if a=="animal":
		requests.get('https://www.fast2sms.com/dev/bulkV2?authorization=gNYhnkTEm37FPDp26SvbjrQ5ysUw9Cl0ecaABXduZH1Gx8ztqIhIXaYnVLO7ps1P8KvtiN9BCDHR5ruJ&route=q&message=Animal Deteted!&language=english&flash=0&numbers=')
		picname=datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
		cv2.imwrite(picname+'.jpg',frame)
		multi_part_upload('gnaneshwar', picname+'.jpg', picname+'.jpg')
		json_document={"link":COS_ENDPOINT+'/'+'gnaneshwar'+'/'+picname+'.jpg'}
		new_document = my_database.create_document(json_document)
		if new_document.exists():
	   		print(f"Document successfully created.")
	cv2.imshow("Final Image",frame)
	temp=random.randint(0,100)
	hum=random.randint(0,100)
	moist=random.randint(0,100)
	myData={'temperature': temp, 'humidity':hum,'moisture':moist}
	client.publishEvent(eventId="status", msgFormat="json", data=myData, qos=0, onPublish=None)
	print("Data published to IBM IoT platfrom: ",myData)
	client.commandCallback = myCommandCallback
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
    
client.disconnect()
cam.release()
cv2.destroyAllWindows()
