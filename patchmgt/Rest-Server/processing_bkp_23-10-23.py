from connect import *
import os
import sys
from loguru import logger as log
from datetime import datetime
import xml.etree.ElementTree as ET
import json
from src.AzureMonitoring.DBClasses import *
import psycopg2
import psycopg2.extras
import xml.etree.ElementTree as ET
import json
import ping3
thresholdProcessQ = asyncio.Queue()

class Processing:

    def __init__(self,config):
        
        self.enbaledParamsList = ['ProcessorUsage','MemoryUsage',\
        'DiskUsagePerDrive','AvailableDisk','NetworkInterfaceInBytesPerInterface',\
        'NetworkInterfaceOutBytesPerInterface','NetworkInterfaceInBytes','NetworkInterfaceOutBytes',\
        'CurrentLogicalDiskQueueLength','AverageLogicalDiskReads','AverageLogicalDiskWrites','Availability','PacketLoss','ResponseTime']

        
        self.devicemodels ={
            'Windows Server 2016':{'2016':'Windows Server 2016'},
            'Windows Server 2019':{'2019':'Windows Server 2019'},
            'Windows Server 2012': {'R2':'Windows Server 2012 R2'},
            'Windows 10': { 'Pro':'Windows 10 Pro'},
            'Windows 8.1':{'8.1':'Windows 8.1'},
            'Windows 11':{'Pro':'Windows 11 Pro'}
        }

        self.connection = Connection(config)
        log.debug("Connection Handler object : {}",self.connection)
    
    async def Init_Connectors_and_Loaders(self,loop):
        await self.connectors(loop)
        await self.loaders()
    
    async def loaders(self):
        await self.load_lastpooltime()
        await self.svc_uid_dict()
        await self.svc_dict()
        await self.load_ip_dict()
        await self.load_uid_dict()
        await self.load_ip_hostanme_dict()
        
    async def connectors(self,loop,flag=0):
        if flag == 0 or flag == 1:
            await self.connection.RMQ_Connection(loop)
        if flag == 0 or flag == 2:
            await self.connection.DB_Connection()

    async def load_ip_dict(self):
        query = "select t1.deviceip, t1.paramname, t1.periodformonitoring, t1.protocol, \
            t2.value1, t3.wqlquery from targetconfigurations as t1 left join threshold as t2 \
            on t2.thresholdkey = t1.thresholdkey left join wmiquerydetails t3 on t1.paramname = t3.paramname  where (t1.protocol='WMI' or t1.protocol='ICMP') \
            and t1.paramname in ('Network Interface Out Bytes: Per Interface',\
            'Current Logical Disk Queue Length' , 'Network Interface In Bytes: Per Interface', \
            'Available Disk' ,'Average Logical Disk Writes','Disk Usage: Per Drive',\
            'Network Interface Out Bytes','Processor Usage','Memory Usage',\
            'Network Interface In Bytes','Average Logical Disk Reads','Availability','PacketLoss','ResponseTime')"
        
        db_targetconf_result = await self.connection.DB_Execute(query)
        self.monDevMetricsParams = self.ip_dict_process(db_targetconf_result, Flag = True)
        log.debug("monitored device with params dict : {}",self.monDevMetricsParams)

        other_query = "select t1.deviceip, t1.paramname, t1.periodformonitoring, t1.protocol, \
            t2.value1, t3.wqlquery from targetconfigurations as t1 left join threshold as t2 \
            on t2.thresholdkey = t1.thresholdkey left join wmiquerydetails t3 on t1.paramname = t3.paramname  where \
            t1.paramname not in ('Network Interface Out Bytes: Per Interface',\
            'Current Logical Disk Queue Length' , 'Network Interface In Bytes: Per Interface', \
            'Available Disk' ,'Average Logical Disk Writes','Disk Usage: Per Drive',\
            'Network Interface Out Bytes','Processor Usage','Memory Usage',\
            'Network Interface In Bytes','Average Logical Disk Reads','Availability','PacketLoss','ResponseTime') and t1.paramname not like '%Service'"

        db_targetconf_otherresult = await self.connection.DB_Execute(other_query)
        self.monOtherDevMetricsParams = self.ip_dict_process(db_targetconf_otherresult, Flag = False)
        log.debug("monitored device with other params dict : {}", self.monOtherDevMetricsParams)

    def get_lastpooltime(self,param_name,ip,isSvc=False):
        if not isSvc:
            if ip in self.lastpooltime:
                if param_name in self.lastpooltime[ip]:
                    return self.lastpooltime[ip][param_name]['lastPolledTime'].strftime("%Y-%m-%dT%H:%M:%SZ")
                else:
                    return None
            else:
                return None
        else:
            for svc_param_name, svc_name in param_name:
                if ip in self.lastpooltime:
                    if svc_param_name in self.lastpooltime[ip]:
                        return self.lastpooltime[ip][svc_param_name]['lastPolledTime'].strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                return None

    
    def ip_dict_process(self,db_targetconf_result, Flag = False):
        ip_dict ={}
        for result in db_targetconf_result:
            param_dict ={}
            sub_param_dict={}
            param_name = result[1].replace(' ','').replace(':','')
            sub_param_dict["ParamName"] = param_name
            sub_param_dict["isMonitoringEnabled"] =True
            sub_param_dict["periodicity"]=str(result[2])
            sub_param_dict["threshold"]=result[4]
            sub_param_dict["QueryType"] = result[3]
            sub_param_dict["QueryText"] = result[5]
            
            sub_param_dict["lastPolledTime"]= self.get_lastpooltime(param_name, result[0])

            if result[0] in ip_dict:
                    param_dict[param_name] =  sub_param_dict
                    ip_dict[result[0]].update(param_dict)
            else :
                    param_dict[param_name] =  sub_param_dict
                    ip_dict[result[0]] = param_dict
        
        if Flag == True:
            for key,param_names in ip_dict.items():
                '''
                 "ProcessorUsage": {
                     "isMonitoringEnabled": True,
                     "periodicity": 60,
                     "threshold ": 90,
                     "lastPolledTime"; "2023-02-01 12:00 AM"
                 }
                 '''
                for param_name in param_names:
                    for enabledParam in self.enbaledParamsList:
                        if param_name == enabledParam:
                            break
                    else:
                        temp_dict ={}
                        temp_dict[enabledParam] = {"ParamName" : param_name, "isMonitoringEnabled": False}
                        ip_dict[key].update(temp_dict)

            for svc_Ip in self.ServiceParms:
                lastpooltime = self.get_lastpooltime(self.ServiceParms[svc_Ip][1]["paramsListNames"],svc_Ip,True)
                self.ServiceParms[svc_Ip][0]['lastPolledTime']=lastpooltime
                if svc_Ip in ip_dict:
                    srv_dict = {"ServiceList": self.ServiceParms[svc_Ip][0]}
                    ip_dict[svc_Ip].update(srv_dict)
                else:
                    log.debug("only service enabled")
                    ip_dict[svc_Ip] = { "ServiceList" :self.ServiceParms[svc_Ip][0]}

        return ip_dict

    async def load_uid_dict(self):
        #query = "select t1.deviceip, t1.devicename, t1.paramname ,\
        #    t2.uid,t3.servicename from targetconfigurations as t1 join parameterconfigurations t2 \
        #    on t1.devicename = t2.devicename and t1.paramname = t2.paramname left join servicerepo t3 on t1.paramname=t3.paramname where t1.protocol='WMI' and \
        #    t1.paramname in ('Network Interface Out Bytes: Per Interface',\
        #    'Current Logical Disk Queue Length' , 'Network Interface In Bytes: Per Interface', \
        #    'Available Disk' ,'Average Logical Disk Writes','Disk Usage: Per Drive',\
        #    'Network Interface Out Bytes','Processor Usage','Memory Usage',\
        #    'Network Interface In Bytes','Average Logical Disk Reads') or  t1.paramname ilike '%Service'"

        # target_conf_query = "select distinct deviceip,devicename from targetconfigurations where protocol='WMI'"
        # param_conf_query = "select distinct devicename, paramname, uid from parameterconfigurations where protocol='WMI' and paramname in  ('Network Interface Out Bytes: Per Interface','Current Logical Disk Queue Length' , 'Network Interface In Bytes: Per Interface', 'Available Disk' ,'Average Logical Disk Writes','Disk Usage: Per Drive','Network Interface Out Bytes','Processor Usage','Memory Usage','Network Interface In Bytes','Average Logical Disk Reads')"
        
        # target_conf_query_result = await self.connection.DB_Execute(target_conf_query)
        # param_conf_query_result = await self.connection.DB_Execute(param_conf_query)
        #query = "select t1.deviceip, t1.devicename, t1.paramname ,\
        #    t2.uid,t3.servicename from targetconfigurations as t1 join parameterconfigurations t2 \
        #    on t1.devicename = t2.devicename and t1.paramname = t2.paramname left join servicerepo t3 on t1.paramname=t3.paramname where (t1.protocol='WMI' or \
        #    t1.protocol='ICMP') and t1.paramname in ('Network Interface Out Bytes: Per Interface',\
        #    'Current Logical Disk Queue Length' , 'Network Interface In Bytes: Per Interface', \
        #    'Available Disk' ,'Average Logical Disk Writes','Disk Usage: Per Drive',\
        #    'Network Interface Out Bytes','Processor Usage','Memory Usage',\
        #    'Network Interface In Bytes','Average Logical Disk Reads','Availability','PacketLoss','ResponseTime') or  t1.paramname ilike '%Service'"

        query="select t1.deviceip, t1.devicename, t1.paramname ,t2.uid,t3.servicename from targetconfigurations as t1 join parameterconfigurations t2 on (t1.devicename = t2.devicename or t2.devicename ='GLOBAL') and t1.paramname = t2.paramname left join servicerepo t3 on t1.paramname=t3.paramname where (t1.protocol='WMI' or t1.protocol='ICMP') and t1.paramname in ('Network Interface Out Bytes: Per Interface','Current Logical Disk Queue Length' , 'Network Interface In Bytes: Per Interface','Available Disk' ,'Average Logical Disk Writes','Disk Usage: Per Drive','Network Interface Out Bytes','Processor Usage','Memory Usage','Network Interface In Bytes','Average Logical Disk Reads','Availability','PacketLoss','ResponseTime') or  t1.paramname ilike '%Service';"
        param_uid_result= await self.connection.DB_Execute(query)
        self.monDevUids = self.uid_dict_process(param_uid_result)
        log.debug("monitored device with uid dict : {}", self.monDevUids)

    async def load_ip_hostanme_dict(self):
        query = "select distinct deviceip, hostname from targetconfigurations"
        query_result = await self.connection.DB_Execute(query)
        self.hostip_dict = self.load_hostip_process(query_result)
        log.debug("hostname ip address dict : {}",self.hostip_dict)

    def load_hostip_process(self, results):
        
        ret_dict= {}
        for result in results:
            ret_dict[result[1]] = result[0]
        return ret_dict

    def uid_dict_process(self,param_uid_result):
        try:
            ret_dict ={}
            for result in param_uid_result:
                '''
                {
                    "10.1.0.27":{
                                    "ProcessorUsage":S1:P4"                    
                                }
                }
                '''
                sub_dict ={ }
                param_name = result[2].replace(' ','').replace(':','')
                sub_dict[param_name] = result[3]
                if result[0] in ret_dict:
                    ret_dict[result[0]].update(sub_dict)
                else:
                    ret_dict[result[0]]= sub_dict
            return ret_dict
   
        except Exception as e:
            log.debug("Exception Received at Loading deviceip_uid dict as -> {}",e)
    
    async def svc_dict(self):
        query = " select t1.deviceip,t2.paramname,t2.servicename from targetconfigurations t1 join servicerepo  t2 on t1.paramname = t2.paramname"
        db_targetconf_result = await self.connection.DB_Execute(query)
        self.ServiceParms = self.svc_dict_process(db_targetconf_result)
    
    def svc_dict_process(self,srv_results):
        ret_dict={}
        ''' 
        {
            "10.1.0.11":{
                "lastPolledTime": None
                "serviceListNames" :
                "Periodictiy": 60
            }
        }

        '''
        try:
            for srv in srv_results:
                
                if srv[0] in ret_dict:
                    ret_dict[srv[0]][0]["serviceListNames"].append(srv[2]) 
                    ret_dict[srv[0]][1]["paramsListNames"].append((srv[1],srv[2]))
                else:
                    servList =[]
                    servList.append(srv[2])
                    paramsList= []
                    paramsList.append((srv[1],srv[2]))
                    sub_dict = [
                                {"serviceListNames":servList,
                                "periodicity": "60",
                                "lastPolledTime": None,
                                "QueryText":"Select Name,State from Win32_Service Where Name = '0'",
                                "QueryType":"WMI",
                                "ParamName":"ServiceList"},
                                {"paramsListNames": paramsList}
                                ]
                    ret_dict[srv[0]] = sub_dict 
            return ret_dict
        except Exception as e:
            log.debug("Exception Received at Loading")

    async def svc_uid_dict(self):
        query = "select t1.deviceip,t2.paramname,t2.servicename,t3.uid from targetconfigurations t1 join servicerepo  t2 on t1.paramname = t2.paramname join parameterconfigurations t3 on t1.devicename = t3.devicename and t1.paramname = t3.paramname where t1.protocol='WMI'"
        db_result = await self.connection.DB_Execute(query)
        self.ServiceUids = self.svc_uid_dict_process(db_result)
        log.debug("svc_uid_dict values {}",self.ServiceUids)
    
    def svc_uid_dict_process(self,db_results):
        '''{
            "10.1.0.11":{"adws" :{
                "uid": "S1:P3"
                "paramName":

            }
            }
        }'''
        ret_dict={}
        for result in db_results:
            sub_dict= {
                "uid" : result[3] ,
                "paramName" : result[1]
            }

            if result[0] in ret_dict:
                ret_dict[result[0]].update({result[2]: sub_dict})
            else :
                ret_dict[result[0]] = { result[2]: sub_dict }
        
        return ret_dict

    async def load_lastpooltime(self):
        #query="select t1.deviceip,t1.uid,max(t1.retrievaltime) from monitoringdata t1 left join parameterconfigurations t2 on t1.uid=t2.uid where t2.protocol='WMI' group by t1.uid, t1.deviceip"
        query = "select t1.deviceip, t2.paramname, t1.uid, max(t1.retrievaltime) from monitoringdata t1 left join parameterconfigurations t2 on t1.uid=t2.uid where (t2.protocol='WMI' or t2.protocol='ICMP') and t2.paramname in ('Network Interface Out Bytes: Per Interface','Current Logical Disk Queue Length' , 'Network Interface In Bytes: Per Interface', 'Available Disk' ,'Average Logical Disk Writes','Disk Usage: Per Drive','Network Interface Out Bytes','Processor Usage','Memory Usage','Network Interface In Bytes','Average Logical Disk Reads','Availability','PacketLoss','ResponseTime') group by t1.uid, t1.deviceip,t2.paramname"
        db_result = await self.connection.DB_Execute(query)
        self.lastpooltime = self.load_lastpooltime_process(db_result)
    
    def load_lastpooltime_process(self, results):
        ret_dict={}
        try:
            for result in results:
                param_dict ={}
                sub_param_dict={}
                sub_param_dict["lastPolledTime"] = result[3]
                param_name = result[1].replace(' ','').replace(':','')
                if result[0] in ret_dict:
                    param_dict[param_name] =  sub_param_dict
                    ret_dict[result[0]].update(param_dict)
                else :
                    param_dict[param_name] =  sub_param_dict
                    ret_dict[result[0]] = param_dict
            return ret_dict

        except Exception as e:
            log.debug("Received Exception as e {}",e)    
        
    def postProcess(self, msg):
        try:
            gomm_msg ={}
            log.debug("In postProcess Method receive a msg :{}", msg)
            conn = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='postgres', database='anuntatech')
            curObj = conn.cursor()
            log.debug("In postProcess Method receive a msg :{}", msg)
            ip =  str(msg['ip'])
            ipAddress = ip.replace('[','').replace(']','').replace('"','')
            log.debug("Going to check {} present is agentdevices table", ipAddress)
            check_query = "select count(*) from agentdevices where deviceip = '{}'".format(ipAddress)
            agentdevice_Count = curObj.execute(check_query)
            agentdevice_Count = curObj.fetchall()
            if agentdevice_Count[0][0] > 0:
                updquery = "update agentdevices set label = 'WMIAGENT',counter='1' where deviceip = '{}'".format(ipAddress)
                log.debug("updquery formed is {}", updquery)
                curObj.execute(updquery)
                conn.commit()
            curObj.close()
            conn.close()
            paramLst=[]
            if msg['hostName'] in self.hostip_dict:
                msg['ip'] = self.hostip_dict[msg['hostName']]
            for paramsData in msg['paramsUsageData']:
                ParamDct=dict()
                paramValues = dict(paramsData)
                ParamDct['UID'],success = self.get_uid(msg['ip'],paramValues['paramName'])
                if not success:
                    log.debug("Error in loading getUid for deviceParam : {} of deviceip:{}",paramValues["paramName"], msg["ip"])
                    log.debug("message to be saved ")
                    continue
                ParamDct['Param'] = paramValues['paramName']

                if paramValues["paramName"]=="DiskUsagePerDrive":
                    result =''
                    for val in paramValues["Value"]:
                        if result=="":
                            result = result + val["Drive"] +"=" + str(val["Value"])
                            print(result)
                        else:
                            result = result + "|" +val["Drive"] +"=" + str(val["Value"])
                            print(result)
                    ParamDct['Value'] = result
                elif paramValues["paramName"] == "Availability" or paramValues["paramName"] == "PacketLoss" or paramValues["paramName"] == "ResponseTime":
                        log.debug("entering into icmp removal")
                        #output = subprocess.Popen(['ping', '-c', '4', msg['ip']],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        #stdout, stderr = output.communicate()
                        output=ping3.ping(msg['ip'])
                        log.debug("ping output.returncode {}",output)
                        if output == 0:
                            log.debug("Please skip why because go_mm do the process ip: {} output.returncode:{}",msg['ip'],output)
                            continue
                        else:
                            #print(f"Ping failed. Error: {str(stderr)}")
                            if paramValues["Error"] == 0:
                                ParamDct['Value']=paramValues["Value"]
                            else:
                                ParamDct['Value']=''
                                log.debug("don't insert the value for error 12")
                elif paramValues["paramName"] == "NetworkInterfaceInBytesPerInterface" or paramValues["paramName"] == "NetworkInterfaceOutBytesPerInterface":
                    print("entering into Networkinterface")
                    result=''
                    for val in paramValues["Value"]:
                        if result=="":
                            result = result + val["InterfaceName"] +"=" + str(val["Value"])
                            print(result)
                        else:
                            result = result + "|" +val["InterfaceName"] +"=" + str(val["Value"])
                            print(result)
                    ParamDct['Value'] = result
                else:
                    ParamDct['Value'] = str(paramValues['Value'])

                ParamDct['Error'] = str(paramValues['Error'])
                self.monDevMetricsParams[msg['ip']][paramValues["paramName"]].update({'lastPolledTime': msg['retrievalTime'] })
                if 'ProcessNameList' in paramValues: 
                    if paramValues['ProcessNameList'] == None or paramValues['ProcessNameList'] =='':
                        log.debug("No need to Process threshold")   
                    else:
                        log.debug("Need to be implement")
                        '''{
                          "paramName":"ProcessorUsage",
                            "uid":
                            "retrievalTime":
                            "ip": ,
                            "version":,
                            "hostname":,
                            "Value":"63",
                            "Error":0,
                            "ProcessNameList":"chrome#18:42,Microsoft.ServiceHub.Controller#1:1,ScriptedSandbox64#1:1,ScriptedSandbox64#3:1,StandardCollector.Service:1,"
                        } '''
                        thresholdmsg={}
                        thresholdmsg["paramName"]=paramValues["paramName"]
                        thresholdmsg["uid"]=ParamDct['UID']
                        thresholdmsg["retrievalTime"]= msg['retrievalTime']
                        thresholdmsg["ip"]=msg['ip']
                        thresholdmsg["version"]=msg['version']
                        thresholdmsg["hostname"]= msg['hostName']
                        thresholdmsg["Value"]= paramValues["Value"]
                        thresholdmsg["Error"]= paramValues['Error']
                        thresholdmsg["ProcessNameList"]= paramValues['ProcessNameList']

                        thresholdProcessQ.put_nowait(thresholdmsg)
                        log.debug("msg sended to threshold Queue")
                paramLst.append(ParamDct)
            for serviceData in msg['serviceStatusData']:
                svcDct = dict()
                svcValues= dict(serviceData)
                log.debug("serviceValue: {}",svcValues)
                if svcValues['serviceName'] in self.ServiceUids[msg['ip']]:
                    svcDct['UID'] = self.ServiceUids[msg['ip']][svcValues['serviceName']]['uid']
                    svcDct['paramName'] = self.ServiceUids[msg['ip']][svcValues['serviceName']]['paramName']
                    svcDct['Value'] = "Running" if svcValues['status'] == 'Running' else 'Stopped'
                    svcDct['Error'] = str(svcValues['Error'])
                paramLst.append(svcDct)

            if "ServiceList" in self.monDevMetricsParams[msg['ip']]:
                self.monDevMetricsParams[msg['ip']]["ServiceList"].update({'lastPolledTime': msg['retrievalTime'] })
            gomm_msg['CallID'] = "123454567"
            gomm_msg['Resp'] = paramLst
            gomm_msg['DeviceIP'] = msg['ip']
            gomm_msg['Retrievaltime'] = str(msg['retrievalTime'])
            gomm_msg['ErrLog'] = []
            return True, gomm_msg
        except Exception as e:
            log.debug("Exception at postProcess Method as -> {}", e)
            return False, None

    async def get_result(self, hostname, version,ip):
        log.debug("ip output is {}",ip)
        typeofip= type(ip)
        log.debug("ip type is {}", typeofip)
        result = {}
        if hostname in self.hostip_dict:
            ip = self.hostip_dict[hostname]
        else:
            #checkQuery = "select count(*) from wmiagentdeviceadditiondetails where deviceip='"+ip +"'"
            ip = tuple(ip)
            if len(ip) == 1:
                checkQuery = "select deviceip,label,msgid from wmiagentdeviceadditiondetails where deviceip ='"+ str(ip[0]) +"'"
            else:
                checkQuery = "select deviceip,label,msgid from wmiagentdeviceadditiondetails where deviceip in" + str(ip)
            log.debug(checkQuery)
            status = await self.connection.DB_Execute(checkQuery)
            if len(status) != 0:
                if len(status) > 1:
                    log.debug("Need to Analyse the wmiagentdeviceadditiondetails table")
                    result["ip"] = ip[0]
                    result["hostname"] = hostname
                    result["version"] = version
                    result["isAddedforMon"]=False
                    result['enabledParamswithPeriodicityinSecs']= {}
                    return result 
                else:
                    log.debug("data present in DB")
                    log.debug("deviceAdditon: {}",status)
                    ip = status[0][0]
                    labelName = status[0][1]
                    requestId = status[0][2]
            else:
                result["ip"] = ip[0]
                result["hostname"] = hostname
                result["version"] = version
                result["isAddedforMon"]=False
                result['enabledParamswithPeriodicityinSecs']= {}
                return result
            getDeviceModelStatus, deviceVersion = self.getDeviceModel(version)
            if not getDeviceModelStatus:
                result["ip"] = ip
                result["hostname"] = hostname
                result["version"] = version
                result["isAddedforMon"]=False
                result['enabledParamswithPeriodicityinSecs']= {}
                return result
            topReq ="<hopDetailsForAutoMonitoring><hopDetail><ipaddress>%s</ipaddress><label>%s</label><hostName>%s</hostName><deviceModel>%s</deviceModel></hopDetail></hopDetailsForAutoMonitoring>"
            Topodict = {}
            Topodict['filter'] = 'dt_execQ'
            Topodict['sender'] = 'TOPOLOGY'
            Topodict['msgId'] = requestId
            Topodict['msgData'] = topReq % (ip,labelName,hostname,deviceVersion)
            log.debug("msgData: {}",Topodict['msgData'])
            Topodict['priority'] = 1
            Topodict['flag'] = 0
            Topodict['msgType'] = 'AUTOMONITORING_WMI_REQUEST'
            Topodict['receiver'] = 'TOPOLOGY'
            Topodict['delivery_tag'] = 'TOPOLOGY'
            await self.connection.RMQ_Sendmessage(Topodict,'dt_execQ')
            await asyncio.sleep(20)

        try:
            log.debug("checking flow")
            result ={}
            result["ip"] = ip
            result["hostname"] = hostname
            result["version"] = version
            if ip in self.monDevMetricsParams:
                otherParamsList = []
                result['isAddedforMon']= True
                result["sendOnlyHistoryData"] = False
                result["historyDataPeriodicity"] = '3600'
                result['enabledParamswithPeriodicityinSecs']= self.monDevMetricsParams[ip]
                try:
                    otherParams_Output = self.monOtherDevMetricsParams[ip]
                    for key, values in otherParams_Output.items():
                        otherParamsList.append(values)
                        result['enabledParamswithPeriodicityinSecs'].update({"OtherParams" :otherParamsList})
                except:
                    log.debug("No new params found")
                result['QueryExcecution'] = []
                return result
            else:
                result["isAddedforMon"]=False
                result['enabledParamswithPeriodicityinSecs']= {}
                return result 

        except Exception as e: 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            errMsg = "Exception in getuid Method as %s %s %s %s"\
                % (e, exc_type, fname, str(exc_tb.tb_lineno))
            log.debug("Expection Received at {}",errMsg)
    
    def get_uid(self,ip,param):
        try:
            if ip in self.monDevUids.keys():
                if param in self.monDevUids[ip].keys():
                    return self.monDevUids[ip][param],True
                else:
                    log.debug("{} Param not found in DBcache for device IP {}", param, ip)
                    return '', False
            else:
                log.debug("{} device IP not found in DBcache", ip)
                return '',False
        except Exception as e:
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # errMsg = "Exception in getuid Method as %s %s %s %s"\
            #     % (e, exc_type, fname, str(exc_tb.tb_lineno))
            # print(errMsg)
            log.debug("Exception in getuid Method as -> {}",e)
    
    async def close_connections(self):
        await self.connection.Close_Connections()
        thresholdProcessQ.put_nowait(None)

    async def thresholdProcess(self):
        try:
            while True:
                msg = await thresholdProcessQ.get()
                thresholdProcessQ.task_done()
                log.debug("msg received on thresholdProcessQ is {}",str(msg))
                '''
                {
                    "paramName":"ProcessorUsage",
                    "uid":
                    "retrievalTime":
                    "ip": ,
                    "version":,
                    "hostname":,
                    "Value":"63",
                    "Error":0,
                    "ProcessNameList":"chrome#18:42,Microsoft.ServiceHub.Controller#1:1,ScriptedSandbox64#1:1,ScriptedSandbox64#3:1,StandardCollector.Service:1,"
                }
                '''
                if msg == None:
                    log.debug("thresholdProcess co-ro ended")
                    dbNotifyQueue.put_nowait(None)
                    # await self.connection.NotifyCur.execute("select Rest_Agent_notify()")
                    # db_out_data = await self.connection.NotifyCur.fetchall()
                    #print(db_out_data)
                    #await self.gen.asend(None)
                    log.debug("why it is happend")
                    break
                listofProcess = msg['ProcessNameList'].split(',')[:-1:]
                values_Insert= list()
                for Process in listofProcess:
                    data= tuple()
                    if Process != '':
                        ProcessName, Value = Process.split(':')
                        #(ProcessName, ProcessUsageValue, uid, alertRaisedon, deviceIp, ParamName)
                        #(chrome#12, 44, S1:P2, retrievaltime, ip, processorUsage)
                        # data[0]=ProcessName
                        # data[1]=Value
                        # data[2]=msg['uid']
                        # data[3]=msg['retrievalTime']
                        # data[4]=msg['ip']
                        # data[5]=msg['ParamName']
                        data= (ProcessName, Value, msg['uid'], msg['retrievalTime'], msg['ip'], msg['paramName'])
                    values_Insert.append(data)
                
                log.debug("values_Insert:{}", values_Insert)

                query = "Insert into ProcessThresholdAlerts Values(%s, %s, %s, %s, %s, %s)"
                await self.connection.DB_Insert(query, values_Insert)
        except Exception as e:
            log.debug(e)
    """
    def getDeviceModel(self,version):
        for devModel in self.deviceModels:
            log.debug("getDeviceModel to be Check: {}", version)
            if devModel in version:
                log.debug("version matched with: {}", devModel)
                return True , devModel
        else:
            log.debug("for {} version deviceModel not found", version)
            return False,''
    """

    def getDeviceModel(self, version):
        try:
            for devModel in self.devicemodels:
                if devModel in version:
                    for subModel in self.devicemodels[devModel]:
                        if subModel in version:
                            print(subModel)
                            return True, self.devicemodels[devModel][subModel]
                    else:
                        return True, devModel
            else:
                log.debug("for {} version deviceModel not found", version)
                return False,''
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            errMsg = "Exception in getDeviceModel Method as %s %s %s %s"\
                % (e, exc_type, fname, str(exc_tb.tb_lineno))
            log.debug("Expection Received at {}",errMsg)

    
    async def DB_Notifty_Status(self):
        try:
        #reload = True
            while True:
                if dbNotifyQueue.empty():
                    poll = self.connection.NofifyConnect.execute("select 1").fetchall()
                    log.debug("DB polling status: {}", poll)
                    await asyncio.sleep(10)
                else:
                                        
                    msg = await dbNotifyQueue.get()
                    dbNotifyQueue.task_done()
                    log.debug("msg received on dbNotifyQueue is {}",str(msg))

                    if msg == None:
                        log.debug(" dbNotifyQueue loop exited")
                        await asyncio.sleep(3)
                        break
                    
                    await self.loaders()
                    await asyncio.sleep(3)
        except psycopg.OperationalError as e:
            log.debug("Exception received at DB_Connection_Closed")
            

        except Exception as e:
            log.debug("Exception received at DB_Notify_Status {}",e)
    

                
    # async def listener(self):
    #     await self.connection.NotifyCur.execute("LISTEN \"MMCHANNEL\"")
    #     self.gen = self.connection.DBconnect.notifies()
    #     print(self.gen)
    #     async for notify in self.gen:
    #             print(notify)
    #             if notify == None:
    #                 print("none condition")
    #                 await self.gen.aclose()
    #             if notify.payload == "targetconfigurations":
    #                 log.debug("reload needed")
    #             elif notify.payload == "RESTCLOSED":
    #                 await self.gen.aclose()

