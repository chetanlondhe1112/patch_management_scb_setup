import asyncio
import os,random
import ssl
import aio_pika
from natsClient import *
#from SCB_Constants import dMsgTypeCnstsDict 
from message_queue_map import *
from msg_format import *
import signal
import natsUtils
import time
import psycopg2
import configparser
import argparse
import datetime
import traceback
from loguru import logger as log
import html
from rmqClient import RMQShovelTransport
import xml.etree.ElementTree as ET
#from natsLogger import log
import json
from datetime import datetime
import calendar
class MessageBus():
      def __init__(self, scb_to_noc_queue, noc_to_scb_queue, signal_flag, config):
         self.scb_to_noc_queue = scb_to_noc_queue
         self.noc_to_scb_queue = noc_to_scb_queue
         self.signal_flag = signal_flag
         self.signal_flag = signal_flag
         self.rabbitQ = config['rabbitMQ']['queueName']

         self.alertQ = config['rabbitMQ']['alertq']
         self.channel = ''
         self.queue = ''
         self.exchange = ''
         self.conection = ''
         self.dbUserName = config['DB']['user_name']
         self.dbPassWord = config['DB']['password']
         self.database = config['DB']['name']
         self.dbport = config['DB']['dbport']
         self.dbhost = config['DB']['host_name']
         self.QuserName = config['rabbitMQ']['userName']
         self.QPassword = config['rabbitMQ']['passWord']
         self.Qhostname = config['rabbitMQ']['rhost']
         self.rmq_noc_to_scb_queue = ''
         self.rmq_scb_to_noc_queue = "rmq_noc_msg_queue"
         self.scbId = config['NATS']['clientName']
         self.priority = 1
         self.flag = 0
         self.seqId = 0
         self.type = 1
         self.delivery_tag = ''
      async def connectRabbitMQ(self, loop):
          try:
             log.debug("triying to establshing connection with rabbitMQ...")
             self.connection = await aio_pika.connect_robust("amqp://{}:{}@{}/".format(self.QuserName,self.QPassword,self.Qhostname), loop=loop)

             log.debug("Sucessfully Connected with RabbitMQ : {}", self.connection)
             #creating channel
             self.channel = await self.connection.channel()
             #creating exchange
             self.exchange = await self.channel.declare_exchange('exchange',auto_delete = True, durable = True)
            #  self.exchange = await self.channel.declare_exchange(
            #     'exchange',auto_delete = True, durable = True
            #        )
             #Declaring Queue
             #self.queue = await self.channel.declare_queue(
             #   "rmq_comm_queue", 
             #   auto_delete=False, 
             #   durable = True, 
             #   
             log.debug("done")
             self.rmq_noc_to_scb_queue = await self.channel.declare_queue(
                "rmq_noc_to_scb_queue", 
                auto_delete=False, 
                durable = True)
             #await self.rmq_noc_to_scb_queue.bind(self.exchange, self.rmq_noc_to_scb_queue)
             #await self.rmq_scb_to_noc_queue.bind(self.exchange, self.rmq_scb_to_noc_queue)
             self.queue = await self.channel.declare_queue(self.rabbitQ, auto_delete=False, durable = True, arguments={
                 'x-message-ttl': 300000, 'x-max-length' : 10000})
             await self.queue.bind(self.exchange, self.rabbitQ)
             self.alertQueue = await self.channel.declare_queue(self.alertQ, auto_delete=False, durable = True, arguments={
                 'x-message-ttl': 300000, 'x-max-length' : 10000})
             await self.alertQueue.bind(self.exchange, self.alertQ) 
             #await self.natsObj.connectNATS()
             #await self.processMessage(queue)
             #await self.processMessage()
             task1 = loop.create_task(self.processRabbitMQMessage())
             task2 = loop.create_task(self.processNOCMessages())
             task3 = loop.create_task(self.bulkInsert())
             task4 = loop.create_task(self.readMessageFromDB())
             task5 = loop.create_task(self.processAlertQueues())
             task6 = loop.create_task(self.receiveNOCMessages())
             task7 = loop.create_task(self.sendMessageToNoc())
             await asyncio.wait([task1, task2, task3, task4, task5, task6, task7])
             while True:
                 await asyncio.sleep(3)
          except Exception as e:
              log.error("An Exceprion Occured.. {}", e)
      async def bulkInsert(self):
          log.debug("Bulk Insertion process is started..")
          msg_data = []
          rabbi_conn_flag = False
          while True:
              if natsUtils.signal_flag == False:
                 if rabbi_conn_flag == False:
                    await self.connection.close()
                    rabbi_conn_flag = True
                 while not self.scb_to_noc_queue.empty():
                      log.debug("Receving signal from signal handler.. Going to start Bulk insertion {}", 
                              self.scb_to_noc_queue.qsize())
                      message = await self.scb_to_noc_queue.get()
                      message = message.decode('utf-8')
                      msg_data.append((message,0,'now'))
                 if len(msg_data) > 0:
                     try:
                         cursor = natsUtils.dbcursor
                         sql_query = "insert into scb_to_noc_nats(data, flags, insertiontime) values (%s, %s, %s)"
                         log.debug("Sql query is {} and msgdata is {}", sql_query, msg_data)
                         cursor.executemany(sql_query, msg_data)
                         natsUtils.dbconnection.commit()
                         log.debug("{} Record succesfully inserted into table", cursor.rowcount)
                         msg_data = ''
                     except Exception as e:
                         log.error("An Exceprion Occured.. {}", e)
                         log.debug(traceback.print_exc())
                 natsUtils.initialize('', True)

              await asyncio.sleep(5)
        
      async def sendMessageToNoc(self):
          log.debug("entering into publish messages into NOC_COMM Queue..")
          #for data in self.scb_noc_queue.get():
          #print(id(scb_to_noc_queue))
          try:
              while True:
                    #print("Loop")
                    message = await self.scb_to_noc_queue.get()
                    log.debug("sucessfully fetch the data from queue...")
                    #print("data is {}".format(message))
                    json_data = load_json(message)
                    if json_data != None:
                       msgType = int(json_data.get("msgType"))
                       msgId = random.randint(0, 1000000000000000)
                       messageData = json_data.get("msgData")
                       log.debug("Validate the XML before publish into Noc_Comm.. {}", messageData)
                       status, value = natsUtils.validateXML(messageData)
                       if status == False:
                          log.debug("XML validation is failed so the message is skipped... {}", value)
                          continue
                       noc_comm_obj = NocCommMessage(self.scbId, msgId, self.priority, self.flag, self.seqId, msgType, self.delivery_tag, messageData, self.type)
                       if msgType == 102001:
                           data = to_json(noc_comm_obj)
                       else:
                           data = html.unescape(to_json(noc_comm_obj))

                       log.debug("final data is {}", data)
                       await self.channel.default_exchange.publish(aio_pika.Message(
                                                  body = (str(data)).encode()
                                                  #content_type='text/plain',
                                                  ),
                                                  self.rmq_scb_to_noc_queue
                                                  )
          except Exception as e:
              log.error("An Exception is occured... {} ", e)
              os.system('systemctl restart scb_nats_comm')
      
      async def processRabbitMQMessage(self):
          log.debug("entering into receive messages from RabbitMQ...")
          async with self.queue.iterator() as queue_iter:
                async for message in queue_iter:
                      async with message.process():
                            #print(message.body)
                            #print("start to put message")
                            #log.debug("@VJ: %s", message.body)
                            await self.scb_to_noc_queue.put(message.body)
                            log.debug("sucessfully put Message {}", message.body)
                            #print(self.scb_noc_queue.get())
                            queue_size = self.scb_to_noc_queue.qsize()
                            log.debug("Queue size is {}", queue_size)
                            if queue_size > 15:
                                os.system('systemctl restart scb_nats_comm')
      async def processAlertQueues(self):
          log.debug("Entering into process alert Queue")
          async with self.alertQueue.iterator() as queue_iter:
                async for message in queue_iter:
                      async with message.process():
                            #print(message.body)
                            #print("start to put message")
                            #log.debug("@VJ: %s", message.body)
                            try:
                                log.debug("@VJ: {}", message.body)
                                #log.debug("@VJ: {}",message)
                                log.debug("@VJ: {}",type(message.body))
                                body=message.body
                                dec=body.decode('utf-8')
                                log.debug("LA {}",dec)
                                msg=json.loads(dec)
                                log.debug("LA msgData {}",msg['msgData'])
                                log.debug("LA msgType {}",msg['msgType'])
                                msgData=ET.fromstring(msg['msgData'])
                                log.debug("LAmsgData {}",msgData)
                                alertType=msgData.find('alertType').text
                                log.debug("alertType {}",alertType)
                                if msg['msgType'] == 22008 and alertType == 'THRESHOLD':
                                    alertUID = msgData.find('alertUid').text
                                    log.debug("alertUID {}",alertUID)
                                    time=msgData.find('time').text
                                    times = time.split(".")
                                    times = times[0].replace("T", " ")
                                    timestamp1 = (times.split(' '))[1].split('.')
                                    target=msgData.find('target')
                                    deviceIP=target.get('deviceIP')
                                    log.debug("LA alertType {} {} {} {}",alertType,time,target,deviceIP)
                                    cursor = natsUtils.dbcursor
                                    cursor.execute("select count(*) from downtimeinfo where deviceip ='"+deviceIP+"'")
                                    count_of_table = cursor.fetchone()[0]
                                    if count_of_table > 0:
                                        cursor.execute("select periodicity, starttime, endtime from downtimeinfo where deviceip = '"+deviceIP+"'")
                                        rows = cursor.fetchone()
                                        periodicity = rows[0]
                                        start_time_once = rows[1]
                                        end_time_once = rows[2]
                                        start_time1 = str(rows[1])
                                        end_time = str(rows[2])
                                        start_time = start_time1.split(' ')
                                        end_time = end_time.split(' ')
                                        if periodicity == 'DAILY':
                                            if start_time[1] < timestamp1[0] and timestamp1[0] < end_time[1]:
                                                log.debug("alert is skipped for DAILY periodicity: {}".format(deviceIP))
                                                cursor.execute("select count(*) from raisedincidentsuid where uniqueid = '"+alertUID+"'")
                                                count_of_table = cursor.fetchone()[0]
                                                if count_of_table > 0:
                                                    cursor.execute("delete from raisedincidentsuid where uniqueid = '"+alertUID+"'")
                                                    natsUtils.dbconnection.commit()
                                                    log.debug("Deleted from raisedincidentsuid table for alertUid: {} from Daily trigger".format(alertUID)) 
                                            else:
                                                await self.scb_to_noc_queue.put(message.body)
                                                log.debug("sucessfully put Message for DAILY periodicity: {}", message.body)

                                        if periodicity == 'WEEKLY':
                                            insertion_day = datetime.strptime(times, '%Y-%m-%d %H:%M:%S').date()
                                            insertion_date = calendar.day_name[insertion_day.weekday()]
                                            start_day=datetime.strptime(start_time1,'%Y-%m-%d %H:%M:%S').date()
                                            start_day_WEEKLY=calendar.day_name[start_day.weekday()]
                                            log.debug("WEEKLY date is {} {} {} {}",insertion_date,insertion_day,start_day_WEEKLY,start_day)
                                            if start_day_WEEKLY == insertion_date:
                                                log.debug("alert is skipped for WEEKLY periodicity: {}".format(deviceIP))
                                                cursor.execute("select count(*) from raisedincidentsuid where uniqueid = '"+alertUID+"'")
                                                count_of_table = cursor.fetchone()[0]
                                                if count_of_table > 0:
                                                    cursor.execute("delete from raisedincidentsuid where uniqueid = '"+alertUID+"'")
                                                    natsUtils.dbconnection.commit()
                                                    log.debug("Deleted from raisedincidentsuid table for alertUid: {} for WEEKLY trigger".format(alertUID))

                                            else:
                                                await self.scb_to_noc_queue.put(message.body)
                                                log.debug("sucessfully put Message for WEEKLY periodicity: {}", message.body)

                                        if periodicity == 'ONCE':
                                            log.debug("ONCE {} {} {}",rows[1],rows[2],times)
                                            log.debug("ONCE is{} {} {}",type(rows[1]),type(rows[2]),type(times))
                                            times = datetime.strptime(times, '%Y-%m-%d %H:%M:%S')
                                            #end_time = datetime.strptime(rows[2], '%Y-%m-%d %H:%M:%S')
                                            #log.debug("ONCE IS {} {} {}",type(start_time),type(end_time),type(times))
                                            if start_time_once < times and times < end_time_once:
                                                cursor.execute("select count(*) from raisedincidentsuid where uniqueid = '"+alertUID+"'")
                                                count_of_table = cursor.fetchone()[0]
                                                if count_of_table > 0:
                                                    cursor.execute("delete from raisedincidentsuid where uniqueid = '"+alertUID+"'")
                                                    natsUtils.dbconnection.commit()
                                                    log.debug("No Need send alert for ONCE periodicity")
                                            else:
                                                await self.scb_to_noc_queue.put(message.body)
                                                log.debug("sucessfully put Message for ONCE periodicity {}", message.body)

                                    else:
                                        log.debug("count_of downtimeinfo table is equals to 0")
                                        await self.scb_to_noc_queue.put(message.body)
                                        log.debug("sucessfully put Message for ONCE periodicity {}", message.body)
                                else:
                                    await self.scb_to_noc_queue.put(message.body)
                                    log.debug("sucessfully put Message {}", message.body)
                                    #print(self.scb_noc_queue.get())
                                    queue_size = self.scb_to_noc_queue.qsize()
                                    log.debug("Queue size is {}", queue_size)
                                    if queue_size > 15:
                                        os.system('systemctl restart scb_nats_comm')
                            except Exception as e:
                                log.error("An Exception is occured... {} ", e)
                                log.debug(traceback.print_exc())

      async def receiveNOCMessages(self):
        try:
            log.debug("Enteirng into receive messages from NOC")
            async with self.rmq_noc_to_scb_queue.iterator() as queue_iter:
                async for message in queue_iter:
                      async with message.process():
                            await self.noc_to_scb_queue.put(message.body)
                            log.debug("sucessfully put Message {}", message.body)
                            #print(self.scb_noc_queue.get())
                            queue_size = self.scb_to_noc_queue.qsize()
                            log.debug("Queue size is {}", queue_size)
                            if queue_size > 15:
                                os.system('systemctl restart scb_nats_comm')

        except Exception as e:
            pass
      async def processNOCMessages(self):
          try:
             log.debug("entering into receive messages from NOC..")
             init_msg_types()
             while natsUtils.signal_flag:
                 message = await self.noc_to_scb_queue.get()
                 try:
                     log.debug("Message received from NOC..")
                     log.debug("message data is {}", message)
                     jsonMsg = load_json(message)
                     log.debug("Json Generation Sucess..")
                     seqId = jsonMsg.get("seqId")
                     msgId = jsonMsg.get("msgId")
                     msgType = jsonMsg.get("msgType")
                     log.debug("msgType{}",msgType)
                     scbId = jsonMsg.get("scbId")
                     flag = 0
                     priority = 1
                     messageData = jsonMsg.get("data")
                     delivery_tag = ''
                     module_name = MsgMapping[msgType].module_name
                     queue_name = MsgMapping[msgType].queue_name
                     sender = "CM"
                     rabbitObj = MessageHandler(queue_name, sender, msgId, messageData, priority, flag, msgType, module_name, delivery_tag)
                     rabbitdata = rabbitObj.to_json()
                     await self.publisMessageTOModules(rabbitdata, queue_name)
                 except Exception as e:
                     log.error("An Exception occured... {}", e)
              #await channel.default_exchange.publish(
              #                     aio_pika.Message(
              #                     body = message,
              #                     routing_key = module_queue ))
             print("Process skipped...")
          except Exception as e:
              print(e)

                                                                 
      async def publisMessageTOModules(self, msg, routing_key):
          msg = html.unescape(msg)
          log.debug("msggg Type is {}",type(msg))
          mess=json.loads(msg)
          log.debug("msggg Type is {}",mess)
          log.debug("Entering into publisMessageTOModules{} {} {} {}",mess,type(mess),mess['msgData'],type(mess['msgData']))
          if mess['msgType'] == 810001:
              msg1=ET.fromstring(mess['msgData'])
              inf=msg1.find('informationSource')
              version=inf.get('version')
              if version == '8.0.0' or version == "8.0" :
                  routing_key='vmwif_execQ'
          elif mess['msgType'] == 81002:
              msgs=ET.fromstring(mess['msgData'])
              info=msgs.find('informationSources')
              inf=info.find('informationSource')
              version=inf.get('version')
              if version == '8.0.0' or version == "8.0" :
                  routing_key='vmwif_execQ'
          elif mess['msgType'] == 71006 and 'api' in mess['msgData']:
              log.debug("COndition checked")
              cursor = natsUtils.dbcursor
              msgData=mess["msgData"]
              msg1 = ET.fromstring(msgData)
              device = msg1.find('deviceTemplateMonitoringRequest')
              deviceInfo = device.find('deviceInfo')
              ip = deviceInfo.find('ipaddress').text
              api = deviceInfo.find('api')
              user = api.find('user').text
              password = api.find('password').text
              val=(ip,user,password,None)
              sql_query1 = "insert into netscalersession(ipaddress, username, password,lbips) values (%s , %s , %s, %s)"
              log.debug("Sql query is {} and msgdata ", sql_query1)
              cursor.execute(sql_query1, val)
              natsUtils.dbconnection.commit()
              log.debug("{} Record succesfully inserted into table", cursor.rowcount)
              routing_key = routing_key
          elif mess['msgType'] == 71008 and 'agent' in mess['msgData']:
              log.debug("Entering 71008 WMI agent device addition...")
              cursor = natsUtils.dbcursor
              reqRoot = ET.fromstring(mess['msgData'])
              ipaddress = reqRoot.find('windowsDeviceMonitoringRequest/deviceInfo/ipaddress').text
              log.debug("Value of Ipaddress{}",ipaddress)
              label =  reqRoot.find('windowsDeviceMonitoringRequest/deviceInfo/agent/label').text
              msgId = mess['msgId']
              log.debug("Value of label{}",label)
              SelTmpTable = "select count(*) from wmiagentdeviceadditiondetails where deviceip = '{}'".format(ipaddress)
              cursor.execute(SelTmpTable)
              Tmp_Count = cursor.fetchall()
              log.debug("Number of Tmp_Count{}",Tmp_Count)
              if Tmp_Count[0][0] == 0:
                  print("No entries present in wmiagentdeviceadditiondetails for" + ipaddress)
                  insTmpQuery = "insert into wmiagentdeviceadditiondetails (deviceip,label,msgid) values('{0}','{1}','{2}')".format(ipaddress,label,msgId)
                  print(insTmpQuery)
                  cursor.execute(insTmpQuery)
                  natsUtils.dbconnection.commit()
              else:
                  print("The given Deviceip  already exist in wmiagentdeviceadditiondetails")
              return
          else:
              routing_key=routing_key
          #msg = html.unescape(msg)
          log.debug("Entering into publisMessageTOModules and message is {} and queuename is {}", msg, routing_key)
          await self.exchange.publish(aio_pika.Message(
                                          bytes(msg,'utf-8'),
                                          content_type='text/plain'),
                                          routing_key)
          log.debug("Message successfully published..")

      async def readMessageFromDB(self):
          try:
             cursor = natsUtils.dbcursor
             log.debug("Entering into collect data from scb_to_noc table")
             while natsUtils.is_nats_connected:
                   query = "select * from scb_to_noc_nats"
                   cursor.execute(query)
                   msg_data = natsUtils.dbcursor.fetchall()
                   for data in msg_data:
                       print(data)
                       creationTime = data[3]
                       currentTime = datetime.datetime.now()
                       timeDifference = currentTime - creationTime
                       timeDifference_seconds = timeDifference.seconds
                       delQuery = "delete from scb_to_noc_nats where seqid = %s"
                       print(timeDifference_seconds)
                       print(data[1])
                       if timeDifference_seconds > 300 and data[1]['msgType'] != 22006:
                          await self.scb_to_noc_queue.put(data[1])
                          cursor.execute(delQuery, (data[0],))
                       else:
                          log.debug("Putting message into scb_to_noc_quea")
                          await self.scb_to_noc_queue.put(data[1])
                          log.debug("Message in queye is {}", self.scb_to_noc_queue.qsize())
                          cursor.execute(delQuery, (data[0],))
                       natsUtils.dbconnection.commit()
          except Exception as e:
              log.error("An Exception Received... {}", e)
              


async def rebootHandler(signum, frame, signal_flag):
    signal_flag = signal_flag
    log.debug("Entering into reboot Handler")
    #natsUtils.initialize(False)
    import os
    pid = os.getpid()
    #while True:
    #    log.debug("waiting for signal from rabbitmq to kill process....")
    #    if natsUtils.rabbit_flag == True:
    #       os.kill(pid, signal.SIGKILL)
    #    await asyncio.sleep(5)
    counter = 0
    while True:
        log.debug("Deleting the rmq shovels")
        if counter == 0:
           status = natsUtils.delete_shovel()
           counter += 1
        os.kill(pid, signal.SIGKILL)
        await asyncio.sleep(5)


async def main(config):
    signal_flag = True
    natsUtils.initialize(True, '',)
    client_1 = config['NATS']['clientName']
    client_2 = config['NATS']['clientName']
    scb_to_noc_queue = asyncio.Queue()
    noc_to_scb_queue = asyncio.Queue()
    log.debug("Registering signal handlers.")
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
                              s, lambda s=s: loop.create_task(rebootHandler(s, loop, signal_flag)))

    msgObj = MessageBus(scb_to_noc_queue, noc_to_scb_queue, signal_flag, config)
    RMQObj = RMQShovelTransport(config)
    #NATSObj = NATSTransport(scb_to_noc_queue, noc_to_scb_queue, signal_flag, config)
    #NATSObj2 = NATSTransport(scb_to_noc_queue, noc_to_scb_queue, signal_flag, config)
    log.debug("Entering into connect with DB...")
    natsUtils.connectToDB(msgObj.dbUserName, msgObj.dbPassWord, msgObj.dbhost, msgObj.dbport, msgObj.database)
    rabbitMQTask = loop.create_task(msgObj.connectRabbitMQ(loop))

    # create shovel fun call
    RMQShovelTask =  loop.create_task(RMQObj.create_rmq_shovel(loop))
    #NATSTask = loop.create_task(NATSObj.connectNATS(loop, client_1))
    #NATSTask_1 = loop.create_task(NATSObj2.connectNATS(loop, client_2))
    await asyncio.wait([rabbitMQTask])#, NATSTask_1])

if __name__ == "__main__":
    #Initialise logger.
    log.debug("That's it, beautiful and simple logging!")
    log.add("/var/log/scb/scb_nats_comm.log", rotation="100 MB", retention=25, compression="gz", enqueue=True)

    try:
       parser = argparse.ArgumentParser(
                               description='Nats-Comm')
       parser.add_argument('--configPath', required=True,
                                       help='Kindly provide the configuration file path..')
       args = parser.parse_args()
       config = configparser.ConfigParser()
       config.read(args.configPath)
       log.debug("Config path is .. [{}]", args.configPath)
       loop = asyncio.get_event_loop()
       loop.run_until_complete(main(config))
       loop.close()
    except Exception as e:
       log.error("An Exception occured.. %s", e)
       track = traceback.format_exc()
       print(track)

