import subprocess
from loguru import logger as log
import aio_pika
import asyncio
import os
import json
from urllib.parse import quote

class RMQShovelTransport():
    def __init__(self, config):
        self.serverUserName = config['NATS']['serverUserName']
        self.serverPassword = quote(config['NATS']['serverPassword'])
        self.serverIP = config['NATS']['serverIP']
        self.port = config['NATS']['port']
        self.clientName = config['NATS']['clientName']
        self.certfile = "?certfile=" + config['NATS']['certfile']
        self.keyfile = "&keyfile=" + config['NATS']['keyfile']
        self.cacertfile = "&cacertfile=" + config['NATS']['cacertfile']
        self.connection_timeout = "&connection_timeout=" + config['NATS']['connection_timeout']
        self.heartbeat = "&heartbeat=" + config['NATS']['heartbeat']
        self.rmq_protocol = "amqp091"
        self.from_noc_dest_queue = "rmq_noc_to_scb_queue"
        self.from_noc_src_queue = self.clientName
        self.to_noc_dest_queue = 'rmq_scb_to_noc_queue'
        self.to_noc_src_queue = 'rmq_noc_msg_queue'
        self.rmq_shovel_command = "rabbitmqctl set_parameter shovel"

    #async def start(self):
    #     task1 = loop.create_task(self.checkrmqshovelstatus(loop))
    #     task2 = loop.create_task(self.delete_rmq_shovel())
    #     task3 = loop.create_task(self.create_rmq_shovel())
    #     await asyncio.wait([task1, task2, task3])

    async def checkRMQShovelHeartBeat(self):
        log.debug("RMQSHovelHeartBeat checking started....") 
        while True:
            status = self.checkrmqshovelstatus()
            if status == True:
                log.debug("SCB COMM is Connected with RMQ Server Using Shovel")
            else:
                log.debug("shovels are not running restarting the module....")
                os.system('systemctl restart scb_nats_comm')
            await asyncio.sleep(10)


    def checkrmqshovelstatus(self, key=None):
        try:
           shovel_status = subprocess.run(["rabbitmqctl shovel_status --formatter json"],check=True,timeout=10,shell=True,stdout=subprocess.PIPE).stdout
           shovel_status = json.loads(shovel_status)
   
           if len(shovel_status) == 0:
               return False
           elif key==None:
               status_code = -1
               for data in shovel_status:
                   if data["state"] == "running" and data["name"] == "from-noc":
                       status_code = status_code + 1
                   elif data["state"] == "running" and data["name"] =="to-noc":
                       status_code = status_code + 1
                   else:
                       pass
               return True if status_code == 1 else False
           else:
               for data in shovel_status:
                   if data["state"] == "running" and data["name"] == key:
                       return True
               else:
                   return False
        except Exception as e:
           log.debug("An Exception Received.. {}", e)

    async def create_rmq_shovel(self, loop):
        try:
           log.debug("entering into create shovel....")
           status = self.checkrmqshovelstatus()
           if status == False:
              log.debug("creating the from-noc shovel...")
              rmq_uri = "amqps://" + self.serverUserName + ":" + self.serverPassword + "@" + self.serverIP + \
                       ":" +  self.port +  self.certfile + self.keyfile + self.cacertfile + self.connection_timeout + self.heartbeat
              log.debug("rmq_uri is : {}", rmq_uri)
              shovel_from_noc ={
                   "src-protocol": self.rmq_protocol,
                   "dest-uri": "amqp://",
                   "dest-queue": self.from_noc_dest_queue,
                   "dest-protocol": self.rmq_protocol,
                   "src-uri": rmq_uri,
                   "src-queue": self.from_noc_src_queue
                    }
              shovel_from_noc = json.dumps(shovel_from_noc)
              log.debug("from noc shovel command is : {}", shovel_from_noc)
              create_from_noc_shovel =  self.rmq_shovel_command + " from-noc " + "'" + shovel_from_noc + "'"
              log.debug("final command to create from-noc is : {}", create_from_noc_shovel)

              create_status_from_noc = subprocess.run([create_from_noc_shovel],shell=True,check=True,stdout=None)
              log.debug("status of creating shovel: {}",create_status_from_noc)
              await asyncio.sleep(10)
              status = self.checkrmqshovelstatus("from-noc")
              if status == True:
                  log.debug("from-noc shovel creation sucessful...")
              else:
                  log.debug("from-noc shovel is not running")
                  raise Exception("from-noc Shovel creation failed")


              log.debug("creating the to-noc shovel...")
              shovel_to_noc = {
                   "src-protocol": self.rmq_protocol,
                   "src-uri": "amqp://",
                   "src-queue": self.to_noc_src_queue,
                   "dest-protocol": self.rmq_protocol,
                   "dest-uri" : rmq_uri,
                   "dest-queue": self.to_noc_dest_queue
                   }
              shovel_to_noc = json.dumps(shovel_to_noc)
              log.debug("to noc shovell command is : {}", shovel_to_noc)
              create_to_noc_shovel = self.rmq_shovel_command + " to-noc " + "'" + shovel_to_noc + "'"
              log.debug("final command to create to-noc is : {}", create_to_noc_shovel)
              create_status_to_noc = subprocess.run([create_to_noc_shovel],shell=True,check=True,stdout=None)
              log.debug("status of creating shovel is : {}", create_status_to_noc)
              await asyncio.sleep(10)
              status = self.checkrmqshovelstatus()
              if status == True:
                  log.debug("to-noc shovel creation succesful.....")
              else:
                  raise Exception("to-noc Shovel creation failed")
              
              task1 = loop.create_task(self.checkRMQShovelHeartBeat())
              await asyncio.wait([task1])
        except Exception as e:
            log.debug("An Exception occured : {}", e)
            os.system('systemctl restart scb_nats_comm')





