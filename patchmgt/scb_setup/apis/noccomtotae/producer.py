from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json
import toml
import datetime as dt

# Load configuration from file
config_file_path = "/root/scb_dev/patch-management-scripting/patchmgt/scb_setup/config/scb_config.toml"
def load_config(config_file=config_file_path):
    """
        Method to read the configuration file
    """
    return toml.load(config_file)

config = load_config()

# Database, API, Rabit, Status log file configuration
rabbitmq_config = config['rabbitmq']

app = FastAPI()

# Pydantic model for the JSON data
class Message(BaseModel):
    cr_id: str
    start_datetime: str
    end_datetime: str
    configuration_file: str
    vm_id: str
    vm_address: str
    logfile: str
    status: str
    logfilepath: str 
    clientid: str
    tool_name: str
    host_name: str
    agent_exe_name: str
    service_display_name: str
    agent_location: str 
    patch_download_path: str 

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
        channel.queue_declare(queue='hello')

        # Convert message to JSON string
        message_dict = message.dict()#.json()
        #message_json = json.loads(message_json)

        # Get current date and time
        current_datetime = dt.datetime.now()

        # Convert dictionary back to JSON
        message_dict["createddate"]=current_datetime.strftime("%d/%m/%Y %H:%M:%S")

        message_dict["flag"] = "N"
        message_json = json.dumps(message_dict)

        print(message_json)

        # Send message to the queue
        channel.basic_publish(exchange='', routing_key='hello', body=message_json)

        # Close the connection
        connection.close()

        return {"status": "Message sent successfully"}
    	#except Exception as e:
   	    #raise HTTPException(status_code=500, detail=str(e))