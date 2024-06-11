import json
from loguru import logger as log

class MessageHandler():
    def __init__(self, queue_name, sender, msgId, messageData, priority, flag, msgType, receiver, delivery_tag):
        #print("Entering into create Message Handler Obj")
        self.filter = queue_name
        self.sender = sender
        self.msgId = msgId
        self.msgData = messageData
        self.priority = priority
        self.flag = flag
        self.msgType = msgType
        self.receiver = receiver
        self.delivery_tag = ''
    def to_json(self):
        #print("entering into load json", self)
        msgDict = vars(self)
        #print(msgDict)
        json_data = json.dumps(msgDict)
        #print("final data is", json_data)
        return json_data
class NocCommMessage():
    def __init__(self, scbId, msgId, priority, flag, seqId, msgType, delivery_tag, messageData, mtype):
        #########print("Entering into create NOCCOMM Object")
        self.clientId = scbId
        self.msgId = msgId
        self.priority =priority
        self.flag = flag
        self.id = seqId
        self.msgType = msgType
        self.delivery_tag = delivery_tag
        self.data = messageData
        self.type = mtype
def to_json(obj):
        #print("entering into load json", obj)
        msgDict = vars(obj)
        #print(msgDict)
        json_data = json.dumps(msgDict)
        #print("final data is", json_data)
        return json_data
def load_json(data):
    try:
       log.debug("Entering into load json messages")
       str_data = data.decode('utf-8')
       if "UTF-8" in str_data:
           str_data = (str_data.replace('<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\n',"")).replace('\\t',"").replace('\\n',"")
       str_data = str_data.encode('utf-8')
       log.debug("string data is {}", str_data)
       log.debug("string data is {}", type(str_data))
       dict_data = json.loads(str_data)
       print("the dict is {} ", dict_data)
       print("the dict is {} ", type(dict_data))
       return dict_data
    except Exception as e:
        log.error("An Exception is occured %s", e)
