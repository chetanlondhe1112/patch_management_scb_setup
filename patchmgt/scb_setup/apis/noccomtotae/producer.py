from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json
import toml
import datetime as dt
from typing import List, Optional

# Load configuration from file
config_file_path = "F:/patch-managment-project-16/patch_main/patch_management_scb_setup/config/scb_config.toml"
def load_config(config_file=config_file_path):
    """
        Method to read the configuration file
    """
    return toml.load(config_file)

config = load_config()

# Database, API, Rabit, Status log file configuration
rabbitmq_config = config['rabbitmq']

app = FastAPI()

class ClientSetting(BaseModel):
    key: str
    value: str
# Pydantic model for the JSON data
class Message(BaseModel):
    #CRId,ClientId,StartDateTime,EndDateTime,DeviceHostName,DeviceIPAddress,CreatedDate,Flag
    crid: str
    clientid: str
    startdatetime: str
    enddatetime: str
    devicehostname: str
    deviceipaddress: str

    #configuration_file: str
    #logfile: str
    #status: str
    #logfilepath: str 
    toolname: str
    hostname: str
    agentexename: str
    servicedisplayname: str
    servicename:str
    agentlocation: str 
    patchdownloadpath: str 

@app.post("/send/")
async def send_message(message: Message):
    	#try:
        # Connect to RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(
		host=rabbitmq_config['noccom_producer']['host'],
    		port=rabbitmq_config['noccom_producer']['port']
		))

        channel = connection.channel()

        # Declare a queue
        channel.queue_declare(queue='tae_queue')

        # Convert message to JSON string
        #message_dict = message.dict()#.json()
        #message_json = json.loads(message_json)

        # Get current date and time
        #current_datetime = dt.datetime.now()

        # Convert dictionary back to JSON
        #message_dict["CreatedDate"]=current_datetime.strftime("%d/%m/%Y %H:%M:%S")

        #message_dict["Flag"] = "N"
        #message_json = json.dumps(message_dict)

        #print(message_json)

        # Send message to the queue
        channel.basic_publish(exchange='', routing_key='tae_queue', body=message.json())

        # Close the connection
        connection.close()

        return {"status": "Message sent successfully"}
    	#except Exception as e:
   	    #raise HTTPException(status_code=500, detail=str(e))