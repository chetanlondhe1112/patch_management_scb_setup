# The TAE Service developed without API communication between postgres database and consumer
# The TAE Service is build to set a commncation service beween noccom and taa (Task Automation Agent) 
import datetime as dt
from datetime import date
import os
import json
import logging
import threading
import toml
from sqlalchemy import create_engine
from pydantic import BaseModel
import pandas as pd
import psycopg2
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
import aiofiles
import pika

# Create a FastAPI instance
app = FastAPI()

# Load configuration from file
scb_config_file_path = "F:/patch-managment-project-16/patch_main/patch_management_scb_setup/config/scb_config.toml"
tae_config_file_path = "F:/patch-managment-project-16/patch_main/patch_management_scb_setup/tae_config/tae_config.toml"

def load_config(config_file=scb_config_file_path):
    """
        Method to read the configuration file
    """
    return toml.load(config_file)

def load_tae_config(config_file=tae_config_file_path):
    """
        Method to read the configuration file
    """
    return toml.load(config_file)

config = load_config()
tae_config = load_tae_config()

# Configure logging
scb_consumer_log = config['log']['rabbitmq_log_path']['scb_consumer_log_path']
print(scb_consumer_log)
# RabbitMQ configuration
rabbitmq_config = config['rabbitmq']

# Database, API, Rabit, Status log file configuration
pg_config = config['database']['cred']
pg_tables = config['database']['tables']
messagetype_config = config['messagetype']
print(pg_tables)
api_config = config['api']['tae_to_agent']
status_log_config = config['log']['status_log_path']
api_log_path = config['log']['api_log_path']['tae_to_agent']

# Directory to save uploaded files
UPLOAD_DIRECTORY = status_log_config['status_log_path']
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Configure logging
get_schedule_data_log_path = api_log_path['get_schedule_path']
status_log_upload_path = api_log_path['status_log_upload_path']

# tae config
tae_settings = tae_config['tae_config']

# deteime object json encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

# Define the request body schema
class DeviceInfo(BaseModel):
    crid: str
    devicehostname: str
    deviceipaddress: str

# Define the response body schema
class ScheduleData(BaseModel):
    crid: str
    startdatetime: str
    enddatetime: str
    configurationfile: str

def send_to_crapproval_sql(data):
    DATABASE_URL =f"postgresql://{pg_config['username']}:{pg_config['password']}@{pg_config['host']}/{pg_config['database']}"
    engine = create_engine(DATABASE_URL)

    current_datetime = dt.datetime.now()

    data["createddate"] = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    data["flag"] = "N"

    # Convert 'startdatetime' and 'enddatetime' to the correct format
    if "startdatetime" in data:
        data["startdatetime"] = dt.datetime.strptime(data["startdatetime"], "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    if "enddatetime" in data:
        data["enddatetime"] = dt.datetime.strptime(data["enddatetime"], "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

    data = pd.DataFrame([data])
    data.to_sql(name=pg_tables['crapprovaldata_tbl'], con=engine, if_exists='append', index=False)

def send_to_crapproval_psql(data):
    DATABASE_URL =f"postgresql://{pg_config['username']}:{pg_config['password']}@{pg_config['host']}/{pg_config['database']}"
    print(DATABASE_URL)
    conn = psycopg2.connect(DATABASE_URL)
    print(conn)
    print(data)
    pg_cur=conn.cursor()

    current_datetime = dt.datetime.now()

    # Convert dictionary back to JSON
    data["createddate"] = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    data["flag"] = "N"

    # Convert 'startdatetime' and 'enddatetime' to the correct format
    if "startdatetime" in data:
        data["startdatetime"] = dt.datetime.strptime(data["startdatetime"], "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    if "enddatetime" in data:
        data["enddatetime"] = dt.datetime.strptime(data["enddatetime"], "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")


    insert_query = """
        INSERT INTO """+str(pg_tables['crapprovaldata_tbl']).lower()+""" (
            crid,clientid,startdatetime,enddatetime,devicehostname,deviceipaddress,createddate,flag
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id;
        """
    # Execute the SQL query
    pg_cur.execute(insert_query, (
        data['crid'],data['clientid'], data['startdatetime'], data['enddatetime'],
        data['devicehostname'], data['deviceipaddress'],
        data['createddate'], data['flag']
    ))
    new_id = pg_cur.fetchone()[0]

    settings_insert_query = """
        INSERT INTO """+str(pg_tables['settings_tbl']).lower()+""" (
            toolname,hostname,agentexename,servicedisplayname,agentlocation,patchdownloadpath,servicename,createddate
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id;
        """
    # Execute the SQL query
    pg_cur.execute(settings_insert_query, (
        data['toolname'],data['hostname'], data['agentexename'], data['servicedisplayname'],
        data['agentlocation'], data['patchdownloadpath'],
        data['servicename'], data['createddate']
    ))

    conn.commit()
    # Fetch the id of the newly inserted row
    return {"Id": new_id}

# Callback function to handle incoming messages
def tae_consumer_callback(ch, method, properties,body):
    tm = dt.datetime.now()
    logging.info(f"[{tm}] Received {body}")
    #try:
    data = json.loads(body)
    logging.info(f"DataFrame created: {data}")
 
    cr_feed = send_to_crapproval_psql(data=data)
    #send_to_crapproval_sql(data)
    logging.info(f"insertion : succed, Id : {cr_feed['Id']}")

    return True
    #except json.JSONDecodeError as json_err:
    #    logging.error(f"Error decoding JSON: {json_err}")
    #except pd.io.sql.DatabaseError as db_err:
    #    logging.error(f"Database error: {db_err}")
    #except Exception as e:
    #    logging.error(f"Unexpected error: {e}")

def tae_consumer():
    #try:  
    # Loading the log generator
    logging.basicConfig(filename=scb_consumer_log, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # postgress connection

    # Connect to RabbitMQ server
    print(rabbitmq_config)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=rabbitmq_config['scb_consumer']['host'],
        port=rabbitmq_config['scb_consumer']['port']
    ))
    channel = connection.channel()
    logging.info("Connected to RabbitMQ server successfully")

    # Declare the queue
    channel.queue_declare(queue=rabbitmq_config['scb_consumer']['queue'])
    logging.info("Queue declared successfully")

    # Set up a consumer and specify the callback function
    channel.basic_consume(queue=rabbitmq_config['scb_consumer']['queue'], on_message_callback=tae_consumer_callback, auto_ack=True)
    print("Consumer set up successfully, waiting for messages")
    logging.info("Consumer set up successfully, waiting for messages")
    channel.start_consuming()

    #except pika.exceptions.AMQPConnectionError as conn_err:
    #    logging.error(f"Connection error with RabbitMQ: {conn_err}")
    #except pika.exceptions.ChannelError as chan_err:
    #    logging.error(f"Channel error with RabbitMQ: {chan_err}")
    #except KeyboardInterrupt:
    #    logging.info("Interrupt received, stopping consumer")
    #    try:
    #        if channel:
    #            channel.stop_consuming()
    #        if connection:
    #            connection.close()
    #        logging.info("RabbitMQ connection closed")
    #    except Exception as e:
    #        logging.error(f"Error closing RabbitMQ connection: {e}")
    #except Exception as e:
    #    logging.error(f"Unexpected error: {e}")
    #finally:
    #    if connection and not connection.is_closed:
    #        connection.close()
    #        logging.info("RabbitMQ connection closed in finally block")

# Background task for consumer
def run_tae_consumer_in_background():
    thread = threading.Thread(target=tae_consumer)
    thread.daemon = True
    thread.start()

# Start the consumer in the background
run_tae_consumer_in_background()

@app.post("/get_schedule_data/", response_model=ScheduleData)
async def get_schedule_data(device_info: DeviceInfo):

    """
        Api to get the scheduled ata from SCB database from TAE
    """

    logging.basicConfig(filename=get_schedule_data_log_path,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s',)

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(f"postgresql://{pg_config['username']}:{pg_config['password']}@{pg_config['host']}/{pg_config['database']}")
        
        # Query the database using pandas
        query = f"""
            SELECT *
            FROM {pg_tables['crapprovaldata_tbl']}
            WHERE devicehostname = '{device_info.devicehostname}'
                AND deviceipaddress = '{device_info.deviceipaddress}' AND crid = '{device_info.crid}' AND flag = 'N'
        """
        settings_query = f"""
            SELECT *
            FROM settings
            ORDER BY id DESC
            LIMIT 1
        """

        df = pd.read_sql(query, conn)
        settings_df = pd.read_sql(settings_query,conn)
        # Close the connection
        conn.close()
        print(df)
        if len(df)==0 or len(settings_df)==0:
            logging.error(f"ScheduleData not found for DeviceHostname : {device_info.devicehostname} and DeviceIPAddress : {device_info.deviceipaddress}")
            raise HTTPException(status_code=404, detail="ScheduleData not found")
        else:
            logging.info(f"Scheduled data sent for DeviceHostname : {device_info.devicehostname} and DeviceIPAddress : {device_info.deviceipaddress}")

            # Extract data from the DataFrame
            print(df)
            response_data = df.iloc[0].to_dict()
            print(settings_df)
            settings_data =settings_df.iloc[0].to_dict()
            print(response_data)
            settings_data['retrychances']=tae_settings['retrytimes']
            settings_data['retrychancestime']=tae_settings['retrytimelapse']
            settings_data['lastdaysofkbavailable']=tae_settings['lastdaysofkb']
            settings_data['requiredfreespacegb']=tae_settings['requireddevicespace']

            return ScheduleData(
                crid=response_data["crid"],
                startdatetime=response_data["startdatetime"].strftime("%Y-%m-%dT%H:%M:%S"),
                enddatetime=response_data["enddatetime"].strftime("%Y-%m-%dT%H:%M:%S"),
                configurationfile=json.dumps(settings_data, cls=CustomJSONEncoder)
            )
    except psycopg2.Error as e:
        logging.error(f"Database error: {str(e)}")

    #except Exception as e:
    #    logging.error(f"Unexpected Error")
    #    raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_status_data/")
async def upload_file(crid: str = Form(...), devicehostname: str = Form(...), status: str = Form(), file: UploadFile = File(...)):

    """
        Api to Upload status log from agent to tae and then to rabitmq scb producer
    """
    logging.basicConfig(filename=status_log_upload_path,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s',)

    try:

        conn = psycopg2.connect(f"postgresql://{pg_config['username']}:{pg_config['password']}@{pg_config['host']}/{pg_config['database']}")

        # Save the uploaded file
        file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
        async with aiofiles.open(file_location, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        logging.info(f"File {file.filename} saved to {file_location}")

        current_datetime=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Update the database with file details
        stmt ="UPDATE {} SET logfilename = '{}', logfilepath = '{}',status='{}',flag = '{}', updateddate='{}' WHERE crid = '{}' and devicehostname = '{}' ;".format(pg_tables['crapprovaldata_tbl'],file.filename,file_location,status,"Y",current_datetime,crid,devicehostname)
        with conn.cursor() as cur:
            cur.execute(stmt)
            conn.commit()
            if cur.rowcount == 0:
                logging.error(f"CRId : {crid} not found")
                raise HTTPException(status_code=404, detail="CRId not found")

        logging.info(f"Database updated for ClientID {crid} with file {file.filename}")

        # Prepare the message to send to RabbitMQ
        message = {
            "crid": crid,
            "status": status,
            "filename": file.filename,
            "file_path": file_location,
            "file_content": content.decode('utf-8'),  # Assuming the file is a text file (e.g., CSV)
            "messagetype" : messagetype_config['status_data']
        }
        message_json = json.dumps(message)

        # Send the message to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                        host=rabbitmq_config["scb_producer"]['host'],
                        port=rabbitmq_config["scb_producer"]['port']
                        ))
        
        channel = connection.channel()
        channel.queue_declare(queue=rabbitmq_config["scb_producer"]['queue'])
        channel.basic_publish(exchange='', routing_key=rabbitmq_config["scb_producer"]['routing_key'], body=message_json)
        connection.close()

        logging.info(f"Message sent to RabbitMQ: {message_json}")

        return {"CRId": crid, "filename": file.filename, "file_path": file_location}

    except psycopg2.Error as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except pika.exceptions.AMQPError as e:
        logging.error(f"RabbitMQ error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RabbitMQ error: {str(e)}")
    #except Exception as e:
    #    logging.error(f"Unexpected error: {str(e)}")
    #    raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print(api_config)
    uvicorn.run(app, host=api_config['host'], port=api_config['port'], log_level="info")