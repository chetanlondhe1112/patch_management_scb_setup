import psycopg2
from io import StringIO
from io import BytesIO
from lxml import etree
from loguru import logger as log
import subprocess
global is_nats_connected
is_nats_connected = False

def initialize(flag = '', rflag = ''):
    global signal_flag
    global rabbit_flag
    global cursor
    signal_flag = flag
    rabbit_flag = rflag
    cursor = cursorObj
def validateXML(data):
    try:
       #response = etree.parse(StringIO(data))
       #data = data.replace('<?xml version="1.0" encoding="UTF-8"?>\n',"")
       #data = (data.replace('\n','')).replace('\t','')
       response = etree.parse(StringIO(data)) 
       return True, response
    except Exception as e:
       return False, e

def cursorObj(connection, cursor):
    global dbconnection
    global dbcursor
    dbconnection = connection
    dbcursor = cursor

def delete_shovel(shovel_list_name=['from-noc','to-noc']):
    log.debug("Entering into delete exisiting shovel")
    count = -1
    for name in shovel_list_name:
        try:
           to_be_del = "rabbitmqctl clear_parameter shovel " + name
           log.debug("command to be executed:", to_be_del)
           dele=subprocess.run([to_be_del], shell=True, check=True, stdout=None)
           log.debug("status of deleting process:", dele)
           count += 1
        except Exception as e:
           log.error("an exception occured.. {}", e)
    if count == 1:
        return True
    else:
        return False

def connectToDB(dbUserName, dbPassWord, dbhost, dbport, database):
    log.debug("dbhost is : {}", dbhost)
    connection = psycopg2.connect(
                                user = dbUserName,
                                password = dbPassWord,
                                host = dbhost,
                                port = dbport,
                                database = database)
    log.debug("Sucessfylly connected with Postgres")
    cursor = connection.cursor()
    cursorObj(connection, cursor)
