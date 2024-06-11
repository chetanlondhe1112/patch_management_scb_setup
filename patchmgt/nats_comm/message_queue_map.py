MsgMapping = {}

class MsgTypeInfo:
    module_name = ""
    queue_name = ""
    description = ""
    msgType = ""
    is_persisted = False

    def __init__(self, module_name, queue_name, msgType, description):
        self.module_name = module_name
        self.queue_name = queue_name
        self.msgType = msgType
        self.description = description


def init_msg_types():
    #RMM
    MsgMapping[11001] = MsgTypeInfo("RMM", "NA", "Req_ScheduleRR", "RMM_REQ_SCHEDULE_RR")
    MsgMapping[12001] = MsgTypeInfo("RMM", "NA", "Resp_ScheduleRR", "RMM_RESP_SCHEDULE_RR")
    MsgMapping[11002] = MsgTypeInfo("RMM", "NA", "Req_ScheduleRR", "RMM_REQ_EXECUTE")
    MsgMapping[12002] = MsgTypeInfo("RMM", "NA", "Resp_ScheduleRR", "RMM_RESP_EXECUTE")
    MsgMapping[11003] = MsgTypeInfo("RMM", "NA", "Req_CancelRR", "RMM_REQ_EXECUTE")
    MsgMapping[12003] = MsgTypeInfo("RMM", "NA", "Resp_CancelRR", "RMM_RESP_EXECUTE")
    #Monitoring Module
    MsgMapping[21001] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_AddTargets", "MM_REQ_ADD_MULTI_TARGET")
    MsgMapping[22001] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_AddTargets", "MM_RESP_ADD_MULTI_TARGET")
    MsgMapping[21002] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_AddTarget", "MM_REQ_ADD_TARGET")
    MsgMapping[22002] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_AddTarget", "MM_RESP_ADD_TARGET")
    MsgMapping[21003] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_DelTarget", "MM_REQ_DELETE_TARGET")
    MsgMapping[22003] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_DelTarget", "MM_RESP_DELETE_TARGET")
    MsgMapping[21004] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_DelTargets", "MM_REQ_DELETE_MULTI_TARGET")
    MsgMapping[22004] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_DelTargets", "MM_RESP_DELETE_MULTI_TARGET")
    MsgMapping[21005] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_ScheduleFlowMonitor", "MM_REQ_SCHEDULE_FLOW_MONITOR")
    MsgMapping[22005] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_ScheduleFlowMonitor", "MM_REQ_SCHEDULE_FLOW_MONITOR")
    MsgMapping[21006] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_DataQuery", "MM_REQ_DATA_QUERY")
    MsgMapping[22006] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_DataQuery", "MM_RESP_DATA_QUERY")
    MsgMapping[21007] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_CancelDataQuery", "MM_REQ_CANCEL_DATA_QUERY")
    MsgMapping[22007] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_CancelDataQuery", "MM_REQ_CANCEL_DATA_QUERY")
    MsgMapping[22008] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_Alert_Event", "MM_RESP_ALERT_EVENT")
    MsgMapping[21009] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_MultiHistoryQuery", "MM_REQ_MULTI_HISTORY_QUERY")
    MsgMapping[22009] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_MultiHistoryQuery", "MM_RESP_MULTI_HISTORY_QUERY")
    MsgMapping[21010] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_InterfaceCustomization", "MM_REQ_INTERFACE_CUSTOMIZATION")
    MsgMapping[22010] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_InterfaceCustomization", "MM_RESP_INTERFACE_CUSTOMIZATION")
    MsgMapping[21011] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_StartDowntime", "MM_REQ_START_DOWNTIME")
    MsgMapping[22011] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_StartDowntime", "MM_RESP_START_DOWNTIME")
    MsgMapping[21012] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_StopDowntime", "MM_RESP_START_DOWNTIME")
    MsgMapping[22012] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_StopDowntime", "MM_REQ_STOP_DOWNTIME")
    MsgMapping[21013] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_UpdateThreshold", "MM_REQ_UPDATE_THRESHOLD")
    MsgMapping[22013] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_UpdateThreshold", "MM_RESP_UPDATE_THRESHOLD")
    MsgMapping[21014] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_UpdateCredentials", "MM_REQ_UPDATE_CREDENTIALS")
    MsgMapping[22014] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_UpdateCredentials", "MM_REQ_UPDATE_CREDENTIALS")
    MsgMapping[21015] = MsgTypeInfo("MM", "mm_cmmsgQ", "Req_HealthMonitor", "MM_REQ_HealthMonitor")
    MsgMapping[22015] = MsgTypeInfo("MM", "mm_cmmsgQ", "Resp_Healthmonitor", "MM_RESP_HealthMonitor")
    #Synthetic Transaction Module
    MsgMapping[31001] = MsgTypeInfo("STM", "stm_execQ", "Req_Schedule_ST_Batch", "STM_REQ_SCHEDULE")
    MsgMapping[32001] = MsgTypeInfo("STM", "stm_execQ", "Resp_Schedule_ST_Batch", "STM_RESP_SCHEDULE")
    MsgMapping[31002] = MsgTypeInfo("STM", "stm_execQ", "Req_Cancel_ST_Batch","STM_REQ_CANCEL" )
    MsgMapping[32002] = MsgTypeInfo("STM", "stm_execQ", "Resp_Cancel_ST_Batch", "STM_RES_CANCEL")
    MsgMapping[31003] = MsgTypeInfo("STM", "stm_execQ", "Req_Get_Historic_Data", "STM_REQ_GET_HISTORIC_DATA")
    MsgMapping[32003] = MsgTypeInfo("STM", "stm_execQ", "Resp_Get_Historic_Data", "STM_RES_GET_HISTORIC_DATA")
    MsgMapping[32004] = MsgTypeInfo("STM", "stm_execQ", "Resp_ST_Alert", "STM_RES_ALERT" )
    MsgMapping[31005] = MsgTypeInfo("STM", "stm_execQ", "Req_STM_Check_For_Resource_Bundle_Update", "STM_REQ_STM_CHECK_FOR_RESOURCE_BUNDLE_UPDATE")
    MsgMapping[31006] = MsgTypeInfo("STM", "stm_execQ", "Req_STA_Update_Resource_Bundle", "STM_REQ_STA_UPDATE_RESOURCE_BUNDLE")
    MsgMapping[31007] = MsgTypeInfo("STM", "stm_execQ", "Req_Poll_STM", "STM_REQ_POLL_STM")
    # MessageTypes for BackupManager
    MsgMapping[41001] = MsgTypeInfo("BM", "NA", "Req_DoBackup", "BM_REQ_TAKECONFIG_BACKUP")
    MsgMapping[42001] = MsgTypeInfo("BM", "NA", "Resp_DoBackup", "BM_RES_TAKECONFIG_BACKUP")
    MsgMapping[41002] = MsgTypeInfo("BM", "NA", "Req_DoRestore", "BM_REQ_DORESTORE_BACKUP")
    MsgMapping[42002] = MsgTypeInfo("BM", "NA", "Resp_DoRestore", "BM_RESP_DORESTORE_BACKUP")
    #Health Module
    MsgMapping[51001] = MsgTypeInfo("HM", "hm_execQ", "Req_RestartSCB", "HEALTH_REQ_RESTART_SCB")
    MsgMapping[52001] = MsgTypeInfo("HM", "hm_execQ", "Resp_RestartSCB", "HEALTH_RESP_RESTART_SCB")
    MsgMapping[51002] = MsgTypeInfo("HM", "hm_execQ", "Req_SCBStatus", "HEALTH_REQ_SCB_STATUS")
    MsgMapping[52002] = MsgTypeInfo("HM", "hm_execQ", "Resp_SCBStatus", "HEALTH_RESP_SCB_STATUS")
    MsgMapping[52007] = MsgTypeInfo("HM", "hm_execQ", "Resp_SCBAlert", "SCB_ALERT_EVENT")
    MsgMapping[52008] = MsgTypeInfo("HM", "hm_execQ", "Resp_SCBDisconnection", "RESP_SCB_DISCONNECTION")
    MsgMapping[51009] = MsgTypeInfo("HM", "hm_execQ", "Req_TechSupport", "REQ_TECH_SUPPORT")
    MsgMapping[52009] = MsgTypeInfo("HM", "hm_execQ", "Resp_TechSupport", "RESP_TECH_SUPPORT")
    MsgMapping[51010] = MsgTypeInfo("HM", "hm_execQ", "Req_PersistentQCount", "REQ_PERSISTENTQ_COUNT")
    MsgMapping[52010] = MsgTypeInfo("HM", "hm_execQ", "Resp_PersistentQCount", "RESP_PERSISTENTQ_COUNT")
    MsgMapping[51011] = MsgTypeInfo("HM", "hm_execQ", "Req_SCBConnStatus", "REQ_SCB_CONN_STATUS")
    MsgMapping[52011] = MsgTypeInfo("HM", "hm_execQ", "Resp_SCBConnStatus", "RESP_SCB_CONN_STATUS")
    #SCB Connection
    MsgMapping[51003] = MsgTypeInfo("CM", "NA", "Req_RegisterSCB", "CONN_REQ_REGISTER_SCB")
    MsgMapping[52003] = MsgTypeInfo("CM", "NA", "Resp_RegisterSCB", "CONN_RESP_REGISTER_SCB")
    MsgMapping[51004] = MsgTypeInfo("CM", "NA", "Req_CloseConn", "CONN_REQ_CLOSE_CONN")
    MsgMapping[52004] = MsgTypeInfo("CM", "NA", "Resp_CloseConn", "CONN_RESP_CLOSE_CONN")
    MsgMapping[51005] = MsgTypeInfo("CM", "NA", "Req_KeepAlive", "CONN_REQ_KEEP_ALIVE")
    MsgMapping[52005] = MsgTypeInfo("CM", "NA", "Resp_KeepAlive", "CONN_RESP_KEEP_ALIVE")
    MsgMapping[52006] = MsgTypeInfo("CM", "NA", "Resp_ConnStatus", "CONN_RESP_CONN_STATUS")
    #CPE messages types (61001...) are skipped

    # Message Types for discovery
    MsgMapping[71001] = MsgTypeInfo("TOPOLOGY", "cpp_execQ", "Req_TopologySweep", "DISCOVERY_REQ_TOPOLOGY_SWEEP")
    MsgMapping[72001] = MsgTypeInfo("TOPOLOGY", "cpp_execQ", "Resp_TopologySweep", "DISCOVERY_RES_TOPOLOGY_SWEEP")
    MsgMapping[71002] = MsgTypeInfo("TOPOLOGY", "cpp_execQ", "Req_TopologyHop", "DISCOVERY_REQ_TOPOLOGY_HOP")
    MsgMapping[72002] = MsgTypeInfo("TOPOLOGY", "cpp_execQ", "Resp_TopologyHop", "DISCOVERY_RES_TOPOLOGY_HOP")
    MsgMapping[72003] = MsgTypeInfo("TOPOLOGY", "cpp_execQ", "Resp_SNMPLabelSuccess", "DISCOVERY_SNMP_LABEL_SUCCESS")
    MsgMapping[72004] = MsgTypeInfo("TOPOLOGY", "cpp_execQ", "Resp_AutomonitoringStatus", "DISCOVERY_AUTOMONITORING_STATUS")
    MsgMapping[72005] = MsgTypeInfo("TOPOLOGY", "cpp_execQ", "Resp_NoAliveIPFound", "DISCOVERY_NO_ALIVE_IP_FOUND")
    MsgMapping[71006] = MsgTypeInfo("TOPOLOGY", "cpp_execQ", "Req_Automonitoring", "DISCOVERY_REQ_AUTOMONITORING")
    MsgMapping[72006] = MsgTypeInfo("TOPOLOGY", "cpp_execQ", "Resp_Automonitoring", "DISCOVERY_RES_AUTOMONITORING")
    MsgMapping[71007] = MsgTypeInfo("TOPOLOGY", "cpp_execQ", "Req_TopologyStopSweep", "DISCOVERY_REQ_TOPOLOGY_STOP_SWEEP")
    MsgMapping[72007] = MsgTypeInfo("TOPOLOGY", "cpp_execQ", "Resp_TopologyStopSweep", "DISCOVERY_RES_TOPOLOGY_STOP_SWEEP")
    # Message Types for WMI Device monitoring
    MsgMapping[71008] = MsgTypeInfo("WMIEXECUTOR", "wmi_execQ", "Req_WMI_Automonitoring", "WMI_REQ_AUTOMONITORING")
    MsgMapping[72008] = MsgTypeInfo("WMIEXECUTOR", "wmi_execQ", "Resp_WMI_Eventmonitoring", "WMI_RES_EVENTMONITORING")
    MsgMapping[72009] = MsgTypeInfo("WMIEXECUTOR", "wmi_execQ", "Resp_WMI_AutomonitoringStatus", "WMI_AUTOMONITORING_STATUS")
    MsgMapping[72013] = MsgTypeInfo("WMIEXECUTOR", "wmi_execQ", "Resp_WMI_Auto_eventlog_monitoringStatus", "WMI_AUTO_EVENTLOG_MONITORING_STATUS")
    # Message Types for VDI Module
    MsgMapping[81001] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Req_VdiDiscovery", "VDI_REQ_DISCOVERY")
    MsgMapping[82001] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Resp_VdiDiscovery", "VDI_REQ_DISCOVERY")
    MsgMapping[81002] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Req_VdiTopology", "VDI_REQ_TOPOLOGY")
    MsgMapping[82002] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Resp_VdiTopology", "VDI_RESP_TOPOLOGY")
    MsgMapping[81003] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Req_VdiTree", "VDI_REQ_TREE")
    MsgMapping[82003] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Resp_VdiTree", "VDI_RESP_TREE")
    MsgMapping[82004] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Resp_VDI_AutomonitoringStatus", "VDI_AUTOMONITORING_STATUS")
    MsgMapping[81005] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Req_VdiSessionCount", "VDI_REQ_SESSIONCOUNT")
    MsgMapping[82005] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Resp_VdiSessionCount", "VDI_RESP_SESSIONCOUNT")
    MsgMapping[81007] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Req_Url_Validation", "VDI_URL_CHECK_VALIDATION")
    MsgMapping[82007] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Resp_Url_Validation", "VDI_URL_CHECK")
    MsgMapping[82008] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Resp_Url_Alert_validation", "VDI_URL_ALERT_CHECK")
    MsgMapping[82009] = MsgTypeInfo("VDIMODULE", "vdm_execQ", "Resp_CP_Resp_Validation", "VDI_CRITICALPARAM_RESPONSE")
    # Message Types for WMI Event monitoring
    MsgMapping[71010] = MsgTypeInfo("EVENTMONITOR", "eventMonitor_execQ", "Req_WMI_Eventmonitoring", "WMI_REQ_EVENTMONITORING")
    MsgMapping[72010] = MsgTypeInfo("EVENTMONITOR", "eventMonitor_execQ", "Resp_WMI_Eventmonitoring", "WMI_RESP_EVENTMONITORING")
    MsgMapping[72011] = MsgTypeInfo("EVENTMONITOR", "eventMonitor_execQ", "Resp_WMI_Eventmonitoring_Alert", "WMI_RES_EVENTMONITORING_ALERT")
    MsgMapping[71012] = MsgTypeInfo("EVENTMONITOR", "eventMonitor_execQ", "Req_WMI_Cancel_Eventmonitoring", "WMI_REQ_CANCEL_EVENTMONITORING")
    MsgMapping[72012] = MsgTypeInfo("EVENTMONITOR", "eventMonitor_execQ", "Resp_WMI_Cancel_Eventmonitoring", "WMI_RES_CANCEL_EVENTMONITORING")
    # Alert Regulator Messages
    MsgMapping[91001] = MsgTypeInfo("ALERTREGULATOR", "alertRegulatorQ", "Req_ChangeRegulationFactor", "AR_REQ_CHANGE_REGULATION_FACTOR")
    MsgMapping[92001] = MsgTypeInfo("ALERTREGULATOR", "alertRegulatorQ", "Resp_ChangeRegulationFactor", "AR_RESP_CHANGE_REGULATION_FACTOR")
    # Message Types for Utility Module
    MsgMapping[101001] = MsgTypeInfo("UTILITY", "um_execQ", "Req_UM_Ping", "UM_REQ_PING")
    MsgMapping[101002] = MsgTypeInfo("UTILITY", "um_execQ", "Req_UM_Nmap", "UM_REQ_NMAP")
    MsgMapping[102001] = MsgTypeInfo("UTILITY", "um_execQ", "Resp_UM_Ping", "UM_RESP_PING")
    MsgMapping[102002] = MsgTypeInfo("UTILITY", "um_execQ", "Resp_UM_Nmap", "UM_RESP_NMAP")
    # Message Types for HealthDiagnostics Module
    MsgMapping[111001] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Req_HMD_Config", "HMD_REQ_CONFIG")
    MsgMapping[112001] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Resp_HMD_Config", "HMD_RESP_CONFIG")
    MsgMapping[112002] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Resp_HMD_Consolidate", "HHD_RES_CONSOLIDATE")
    MsgMapping[111003] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Req_HMD_History", "HMD_REQ_HISTORY")
    MsgMapping[112003] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Resp_HMD_history", "HMD_RES_HISTORY")
    MsgMapping[111004] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Req_HMD_Exclusion", "HMD_REQ_EXCLUSION")
    MsgMapping[112004] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Resp_HMD_Exclusion", "HMD_RES_EXCLUSION")
    MsgMapping[111005] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Res_HMD_EngineerL1", "HMD_RES_ENGINEERL1")
    MsgMapping[112006] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Res_HMD_EngineerL2", "HMD_RES_ENGINEERL2")
    MsgMapping[31008] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Req_NetScaler", "REQ_NETSCALER_DETAILS")
    MsgMapping[32008] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Resp_NetScaler", "RESP_NETSCALER_DETAILS")
    MsgMapping[991001] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Req_CSAT", "REQ_CSAT_DETAILS")
    MsgMapping[991002] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Resp_CSAT", "RESP_CSAT_DETAILS")
    MsgMapping[992002] = MsgTypeInfo("HEALTHDIAGNOSTICS", "hd_execQ", "Resp_CSAT_POPUP", "REQ_CSAT_POPUP_DETAILS")
    #Message types for Azure MM
    MsgMapping[121001] = MsgTypeInfo("AZUREMM", "azuremm_execq", "Req_WVD_Config", "WVD_REQ_CONFIG")
    MsgMapping[122001] = MsgTypeInfo("AZUREMM", "azuremm_execq", "Resp_WVD_Config", "WVD_RESP_CONFIG")
    MsgMapping[121002] = MsgTypeInfo("AZUREMM", "azuremm_execq", "Req_WVD_Config_Session", "WVD_REQ_CONFIG_SESSION")
    MsgMapping[122002] = MsgTypeInfo("AZUREMM", "azuremm_execq", "Resp_WVD_Config_Session", "WVD_RESP_CONFIG_CONFIG_SESSION")
    MsgMapping[121003] = MsgTypeInfo("AZURE_METRICS_COLLECTOR", "azure_metric_execQ", "Req_AzureMetrics", "AZURE_METICS_DASHBOARD")
    MsgMapping[122003] = MsgTypeInfo("AZURE_METRICS_COLLECTOR", "azure_metric_execQ", "Resp_AzureMetrics", "AZURE_METICS_DASHBOARD")
    MsgMapping[122004] = MsgTypeInfo("AZURE_METRICS_COLLECTOR", "azure_metric_execQ", "Resp_AzureMetrics_DeviceAdd", "AZURE_METICS_DEVICE_ADD_ALERT")
    MsgMapping[122005] = MsgTypeInfo("AZUREMM", "azuremm_execq", "Resp_WVD_NSG_Alert", "WVD_RESP_NSG_ALERT")

    #CommModule Special messages
    MsgMapping[10001] = MsgTypeInfo("CM", "NA", "ACK", "ACK_MSG")




if __name__ == "__main__":
    init_msg_types()
    print(MsgMapping[81001].queue_name)
