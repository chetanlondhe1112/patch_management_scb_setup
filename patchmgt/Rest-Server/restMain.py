#FastApi imports
from typing_extensions import Annotated
from fastapi import FastAPI, Query
from typing import List , Union
from pydantic import BaseModel

#HyperCorn imports
from hypercorn.config import Config
from hypercorn.asyncio import serve

#Other libs
from loguru import logger as log
import asyncio
import signal
import json  
import configparser

#import from other files
from processing import *

app = FastAPI()
postProcessingQ = asyncio.Queue()

class Parms(BaseModel):
    paramName:str
    Value:Union[str, list]= None
    Error:int
    ProcessNameList:str = None

class Services(BaseModel):
    serviceName:str
    status:str
    Error:int

class PostData(BaseModel):

    ip:str
    hostName:str
    version:str
    retrievalTime:str
    paramsUsageData:List[Parms]
    serviceStatusData:List[Services] = None
    powershellExecutionDatas :list = None

    class Config:
        arbitrary_types_allowed=True


@app.get("/getDeviceStatus")
async def getStatus(ip: List[str] =Query(None), version = None, hostname = None):
    try:
        log.debug("ip output is {}",ip)
        typeofip= type(ip)
        log.debug("ip type is {}", typeofip)
        ip = (((ip[0].replace('[','')).replace(']', '')).replace('"', "")).split(',')
        log.debug("Device IP: {0} Windows Version: {1} HostName: {2}", ip, version, hostname)
        ret_data = await oRestHandler.get_result(hostname, version, ip)
        log.debug("return result for deviceip:{0} Value: {1}",ip, ret_data)
        return ret_data
    except Exception as e:
        log.debug("Exception in getStatus Method as -> {}",e)

@app.post("/postMetricsData")
async def postdata(metricData: List[PostData]):
    try:
        log.debug("In postdata Received metricsData PostData is: {}", PostData)
        Res={}
        Res['status']='Accepted'
        log.debug("In postdata Received metricsData is: {}", metricData)
        for data in metricData:
            postProcessingQ.put_nowait(data.__dict__)
        return Res
    except Exception as e:
        log.debug(e)
        Res['status']='Rejected'
        return Res

@app.get("/pingIcmpDetails")
async def icmpData():
    try:
        log.debug("icmpData get started")
        Resp={}
        Resp['status']='ok'
        log.debug("In icmpData Received icmpData: {}",icmpData)
        return Resp
    except Exception as e:
        log.debug(e)
        Resp['status']='not ok'
        return Resp

def _signal_handler(*_: any ) -> None:
        log.debug("shutdown event trigerred")
        global shutdown
        shutdown = True
        postProcessingQ.put_nowait(None)
        thresholdProcessQ.put_nowait(None)
        #asyncio.run(oRestHandler.gen.aclose())
        shutdown_event.set()

async def queueConsume():
    while True:
        msg = await postProcessingQ.get()
        postProcessingQ.task_done()
        log.debug("msg received on postProcessingQ is {}",str(msg))

        if msg == None:
           #await loop.shutdown_asyncgens()
           log.debug("loop exited")
           await asyncio.sleep(3)
           break
        
        status, dict_msg = await oRestHandler.postProcess(msg)
        log.debug("PostProcess Status: {}", status)
        log.debug("dict_msg to be send to mm: {}", dict_msg)
        
        # dict_msg = 
        # {
        #        "CallID":"12345",
        #        "Resp":[{"Param":"Availability","UID":"S1:P1","Value":"0","Error":"1"}],
        #        "DeviceIP":"127.0.0.1",
        #        "Retrievaltime":'2021-02-18T21:54:42Z',
        #        "ErrLog":[]
        # }
        if status:
            await oRestHandler.connection.RMQ_Sendmessage(dict_msg,'mm_pollQ')
        else:
            log.debug("Error in postprocess ")

async def main():
    await oRestHandler.Init_Connectors_and_Loaders(loop=loop) 
    hyperRest=loop.create_task(serve(app, hyper_config, shutdown_trigger=shutdown_event.wait))
    consumer = loop.create_task(queueConsume())
    threshold_consumer = loop.create_task(oRestHandler.thresholdProcess())
    Db_notifier = loop.create_task(oRestHandler.DB_Notifty_Status())
    await asyncio.wait([Db_notifier,hyperRest,consumer,threshold_consumer])
    await  oRestHandler.close_connections()
    log.debug("service ended")


if __name__ == "__main__":
    #Initialise logger.
    log.add("/var/log/scb/scb_rest_server_new_test.log", rotation="100 MB", retention=25, compression="gz", enqueue=True)

    config = configparser.ConfigParser()
    config.read("/root/anuntatech3/conf/SCBConfiguration.ini")

    oRestHandler = Processing(config)

    hyper_config = Config()
    hyper_config.bind = ["0.0.0.0:8443"]

    shutdown_event = asyncio.Event()

    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, _signal_handler)
    loop.run_until_complete(main())
    loop.close()

