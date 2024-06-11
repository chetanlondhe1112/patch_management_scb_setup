import asyncio
from loguru import logger as log
import aio_pika
import psycopg
import json
dbNotifyQueue = asyncio.Queue(maxsize=1)
class Connection:

    def __init__(self,config):
        self.db_username = config['DB']['user_name']
        self.db_password = config['DB']['password']
        self.db_database = config['DB']['name']
        self.db_port = config['DB']['dbport']
        self.db_host = config['DB']['host_name']

        self.rmq_username = config['rabbitMQ']['userName']
        self.rmq_password = config['rabbitMQ']['passWord']
        self.rmq_hostname = config['rabbitMQ']['rhost']

        self.reloading = True
    
    async def RMQ_Connection(self,loop):
        self.RMQ_connection= await aio_pika.connect_robust("amqp://{}:{}@{}/".format("guest","guest","localhost"), loop=loop)
        self.RMQ_channel = await self.RMQ_connection.channel()

    async def DB_Connection(self):
        self.DBconnect = await psycopg.AsyncConnection.connect("dbname = 'anuntatech' user = 'postgres'\
                         host = 'localhost' password = 'postgres'", autocommit=True)
        self.NofifyConnect = psycopg.connect("dbname ='anuntatech' user ='postgres' host='localhost' password='postgres'",autocommit=True)

        #self.NotifyCur = self.Notifyconnect.cursor()
        self.NofifyConnect.execute("LISTEN \"MMCHANNEL\"")
        #await self.NotifyCur.execute("LISTEN \"MMCHANNEL\"")
        #self.DBconnect.add_notify_handler(self.db_notify)
        self.NofifyConnect.add_notify_handler(self.DB_Notify)
        self.DBCur = self.DBconnect.cursor()
        log.debug("Connection Class Ended")

    async def RMQ_Sendmessage(self,dict_msg,key):
        await self.RMQ_channel.default_exchange.publish(
            aio_pika.Message(
                content_type="text/plain",
                body=json.dumps(dict_msg).encode()
            ),
            routing_key=key
        )
        log.debug("msg sended")
    
    #async def DB_Execute(self,query):
        #await self.DBCur.execute(query)
        #db_out_data = await self.DBCur.fetchall()
        #print(type(self.DBCur))
        #return db_out_data
    async def DB_Execute(self,query):
        try:
            log.debug("executing query :%s",query)
            async with self.DBconnect.transaction():
                log.debug("into transaction")
                async with self.DBconnect.cursor() as cur:
                    log.debug("into dbconnect cursor {}:",cur)
                    await cur.execute(query)
                    db_out_data = await cur.fetchall()
                    log.debug("after execute query {}",db_out_data)
            #cur=await self.DBCur
                #await cur.execute(query)
                #db_out_data = await cur.fetchall()
            log.debug("query execution successful")
            return db_out_data
        except Exception as e:
            log.debug("Error in DB_Execute: %s",e)
            return None


    async def DB_Insert(self, insert_query, values):
        try:
            await self.DBCur.executemany(insert_query, values)
            db_out_data = await self.DBCur.fetchall()
            print(db_out_data)
            return True
        except Exception as e:
            log.debug(e)
            return False
    
    def DB_Notify(self,notify):
        log.debug(notify)           
        if notify.payload == "targetconfigurations":
            if dbNotifyQueue.empty():
                dbNotifyQueue.put_nowait("reload")
                log.debug("put data to reloading")
        elif notify.payload == "RESTCLOSED":
            log.debug("reload neededed")

    async  def Close_Connections(self):
        await self.RMQ_channel.close()
        await self.RMQ_connection.close()
        
        self.NofifyConnect.close()
        await self.DBCur.close()

        await self.DBconnect.close()
        log.debug("Rabbitmq and Database Connection is Closed")


    
