from loguru import logger as log

deviceModels =[ 'Windows Server 2016', \
                'Windows Server 2019',\
                'Windows Server 2022', \
                'Windows Server 2012', \
                'Windows 10',\
                'Windows 11', \
                'Windows 8.1']
#version= 'Microsoft Windows Server 2022 Datacenter'

def checkdevModel(version):
    for devModel in deviceModels:
        print("devicemodel to check",devModel)
        if devModel in version:
            print(devModel)
            return devModel
    else:
        print("nothing found")


def postProcess(msg,getuid):
        try:
            finalValues={}
            log.debug(msg)
            paramLst=[]
            for paramsData in msg['paramsUsageData']:
                ParamDct=dict()
                paramValues = dict(paramsData)
                print("entering into msg.paramsusagedata")
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
                ParamDct['UID'] = get_uid(msg['ip'],paramValues['paramName'])
                ParamDct['Error'] = str(paramValues['Error'])
                paramLst.append(ParamDct)

            finalValues['CallID'] = "123454567"
            finalValues['Resp'] = paramLst
            finalValues['DeviceIP'] = msg['ip']
            finalValues['Retrievaltime'] = str(msg['retrivalTime'])
            finalValues['ErrLog'] = []
        except Exception as e:
            print(e)
        return finalValues


