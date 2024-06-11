pass
# import ssl
# from natsMain import *
# from natsMain import log
# from nats.aio.client import Client as NATS
# from stan.aio.client import Client as STAN
# from nats.aio.errors import NatsError
# from msg_format import *
# import natsUtils
# from loguru import logger as log
# #from natsLogger import log
# import os
# import random


# #import commands
# class NATSTransport():
#     def __init__(self, scb_to_noc_queue, noc_to_scb_queue, signal_flag, config):
#         self.ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
#         self.ssl_ctx.load_verify_locations('src/nats_comm/ca.pem')
#         self.scbId = config['NATS']['clientName']
#         self.priority = 1
#         self.flag = 0
#         self.seqId = 0
#         self.type = 1
#         self.delivery_tag = ''
#         self.serverUserName = config['NATS']['serverUserName']
#         self.serverPassword = config['NATS']['serverPassword']
#         self.serverIP = config['NATS']['serverIP']
#         self.port = config['NATS']['port']
#         self.clientName = config['NATS']['clientName']
#         self.clientName_1 = config['NATS']['clientName']
#         self.clientURI = config['NATS']['clientName']
#         self.clusterName = config['NATS']['clusterName']
#         self.nocCommURI = config['NATS']['nocCommURI']
#         self.scb_to_noc_queue = scb_to_noc_queue
#         self.noc_to_scb_queue = noc_to_scb_queue
#         self.signal_flag = signal_flag
#         self.sc = ''
#         self.nc = ''
#     async def connectNATS(self, loop, client_id):
#         try:
#             log.error("Entering into connect NATS Straming Server..")
#             self.nc = NATS()
#             serverURI = 'tls://' + self.serverUserName + ':' + self.serverPassword + '@' + self.serverIP + ':' + self.port
#             #print(serverURI)
#             async def log_nats_error(e):
#                 log.error("exception occured {}", e)
#                 os.system('systemctl restart scb_nats_comm')
#             connect = await self.nc.connect(serverURI, tls = self.ssl_ctx, io_loop = loop, 
#                     max_reconnect_attempts = 1, error_cb = log_nats_error, connect_timeout = 10)
#             log.debug("@VJ : nats connection is {}", self.nc)
#             self.sc = STAN()
#             await self.sc.connect(self.clusterName, client_id, nats = self.nc)
#             await self.sc.subscribe(self.clientURI, cb=self.NATSCallBack, durable_name = "test_durable")
#             log.debug("Successfully connected with nats streaming server : {}", self.sc._conn_id)
#             natsUtils.is_nats_connected = True
#             task1 = loop.create_task(self.sendMessage())
#             task2 = loop.create_task(self.checkConnectionStatus(loop))
#             await asyncio.wait([task1, task2])
#         except NatsError as e:
#             log.error("An exception occured : {}", e)
#             await self.reconnectNats(loop)
#     async def checkConnectionStatus(self, loop):
#         try:
#            while True:
#                if self.nc.is_connected == True:
#                   log.debug("Nats client is connected with NATS Server...")
#                else:
#                    log.debug("Connection lost....")
#                    #await self.reconnectNats(loop)
#                    os.system('systemctl restart scb_nats_comm')
#                await asyncio.sleep(10)
#         except Exception as e:
#                log.debug("An Exception Received.. {}", e)

#                #self.reconnectNats(loop)
#     async def reconnectNats(self, loop):
#         #await self.connectNATS(loop, self.clientName)
#         await self.checkConnectionStatus(loop)

#     async def sendMessage(self):
#           log.debug("entering into publish messages into NOC_COMM Queue..")
#           #for data in self.scb_noc_queue.get():
#           #print(id(scb_to_noc_queue))
#           try:
#               while natsUtils.signal_flag:
#                  if self.nc.is_connected == True:
#                     #print("Loop")
#                     message = await self.scb_to_noc_queue.get()
#                     log.debug("sucessfully fetch the data from queue...")
#                     #print("data is {}".format(message))
#                     json_data = load_json(message)
#                     if json_data != None:
#                        msgType = json_data.get("msgType")
#                        msgId = random.randint(0, 1000000000000000)
#                        messageData = json_data.get("msgData")
#                        log.debug("Validate the XML before publish into Noc_Comm.. {}", messageData)
#                        status, value = natsUtils.validateXML(messageData)
#                        if status == False:
#                           log.debug("XML validation is failed so the message is skipped... {}", value)
#                           continue
#                        noc_comm_obj = NocCommMessage(self.scbId, msgId, self.priority, self.flag, self.seqId, msgType, self.delivery_tag, messageData, self.type) 
#                        data = to_json(noc_comm_obj) 
#                        log.debug("final data is {}", data)
#                        if self.nc.is_connected == True:
#                           await self.sc.publish(self.nocCommURI, data.encode())
#                           log.debug("message published...")
#                        else:
#                            log.debug("Connection lost")
#                            raise Exception("Connection lost")
#           except Exception as e:
#               log.error("An Exception is occured... %s", e)
#               os.system('systemctl restart scb_nats_comm')
#     async def NATSCallBack(self, msg):
#         log.debug("entering into NATSCallBack to recevie messages from NOC...")
#         if natsUtils.signal_flag == True:
#            try:
#                log.debug("Going to insert msg in queue {}", msg.data)
#                await self.noc_to_scb_queue.put(msg.data)
#                log.debug("Sucessfully insert message in queue..")
#            except Exception as e:
#                log.debug("An exception is occured.. {}", e)
#         else:
#                log.debug("trying to close NATS server connection")
#                await self.nc.close()
#                log.debug("Server Connection succesfully stopped")

        

