#!/usr/bin/pypy
import subprocess
import stackless

class SNMPDevice:
    namespace = ""
    vethname = ""
    conffile = ""
    hostname = ""

snmp_devices = {}
ip_range = "192.127.27.%d/24"
bridgename = "snmpsimbridge"
bridge_ip = "192.127.27.227"
bridge_ip_net = "192.127.27.227/24"


def execcmd(cmd):
    print("executing cmd %s" % (cmd))
    subprocess.call(cmd, shell=True)

"""
ip netns add namespace1
ip netns add namespace2
"""
def create_namespaces(num):
    for i in range(1, num+1):
        nsadd = "ip netns add namespace%d" % (i)
        execcmd(nsadd)
"""
# Create the two pairs.
ip link add veth1 type veth peer name br-veth1
ip link add veth2 type veth peer name br-veth2

# Associate the non `br-` side
# with the corresponding namespace
ip link set veth1 netns namespace1
ip link set veth2 netns namespace2

ip netns exec namespace1 ip addr add 192.168.1.11/24 dev veth1

# Set the bridge veths from the default
# namespace up.
ip link set br-veth1 up
ip link set br-veth2 up

# Set the veths from the namespaces up too.
ip netns exec namespace1 ip link set veth1 up
ip netns exec namespace2 ip link set veth2 up

"""
def setup_veth_per_ns(num):
    for i in range(1, num+1):
        vethadd = "ip link add veth%d type veth peer name br-veth%d" % (i, i)
        execcmd(vethadd)
        setns = "ip link set veth%d netns namespace%d" % (i, i)
        execcmd(setns)
        address = ip_range % (i)
        addip = "ip netns exec namespace%d ip addr add %s dev veth%d" % (i, address, i)
        execcmd(addip)
        brlinkup = "ip link set br-veth%d up" % (i)
        execcmd(brlinkup)
        vethup = "ip netns exec namespace%d ip link set veth%d up" % (i, i)
        execcmd(vethup)

"""
# Create the bridge device naming it `br1`
# and set it up:
ip link add name br1 type bridge
ip link set br1 up
ip addr add 192.168.1.1/24 brd + dev br1

# Add the br-veth* interfaces to the bridge
# by setting the bridge device as their master.
ip link set br-veth1 master br1
ip link set br-veth2 master br1
"""
def setup_linux_bridge(num):
    createbridge = "ip link add name %s type bridge" % (bridgename)
    bridgelinkup = "ip link set %s up" % (bridgename)
    setbrigeip = "ip addr add %s brd + dev %s" % (bridge_ip_net, bridgename)
    execcmd(createbridge)
    execcmd(bridgelinkup)
    execcmd(setbrigeip)
    for i in range(1, num +1 ):
        addvethtobr = "ip link set br-veth%d master %s" % (i, bridgename)
        execcmd(addvethtobr);

"""
ip -all netns exec ip route add default via 192.168.1.10
"""
def add_default_routes_to_ns():
    execcmd("ip -all netns exec ip route add default via %s" % (bridge_ip))


"""
# Enable routing and NAT.
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -j MASQUERADE
# Enable ipv4 ip forwarding
sysctl -w net.ipv4.ip_forward=1
"""
def enable_routing_n_nat():
    enablert = "sysctl -w net.ipv4.ip_forward=1"
    execcmd(enablert)
    ipnetwork = ip_range % (0)
    enablenat = "iptables -t nat -A POSTROUTING -s  %s -j MASQUERADE" % (ipnetwork)
    execcmd(enablenat)

'''conf_template = """
# mini-snmpd.conf: Example
hostname       = "%s"
location       = "Exampleville Site 1."
contact        = "ops@example.com"
description    = "NAS monitor"

# Vendor OID tree
vendor         = ".1.3.6.1.4.1.4.1.1"

# true/false, or yes/no
authentication = true
#f1rsts0urc3@dm!n
community      = "public"

# MIB poll timeout, sec
timeout        = 200

# Disks to monitor, i.e. mount points in UCD-SNMP-MIB::dskTable
disk-table     = { "/", }

# Interfaces to monitor, currently only for IF-MIB::ifTable
iface-table    = { "%s", "lo" }
"""'''
conf_template = """[postgres]
dbUserName=postgres
dbPassWord=postgres
database=anuntatech
dbport=5432
dbhost=192.168.231.112

[rabbitMQ]
queueName = %s
protocol = admp
userName = guest
passWord = quest
rhost = 192.168.231.112
auto_delete = True
durable = True

[NATS]
certificate_path = ''
serverUserName = anunta
serverPassword = anunta@123
serverIP = 192.168.231.112
port = 443
clientName = %s
clientURI = %s
clusterName = test-cluster
nocCommURI = NocComm
"""

def start_minisnmpd_per_ns(num):
    for i in range(1, num+1):
        queueName = "Nats_Queues%d" % (i)
        clientName = "testNats%d" % (i)
        clientURI = "testNats%d" % (i)
        confFile = "natsConf%d.ini" % (i)
        #hostname = "minisnmplinux%d" % (i)
        #interface = "veth%d" % (i)
        new_conf = conf_template % (queueName, clientName, clientURI)
        fout = open(confFile, 'w')
        fout.write(new_conf)
        fout.close()
        task = stackless.tasklet(execcmd)
        #minisnmpstart = "ip netns exec namespace%d ./mini_snmpd -f %s -I %s -n &" % (i, hostname, interface)
        minisnmpstart = "ip netns exec namespace%d python3.6 natsMain.py --configPath %s&" % (i, confFile)
        task.setup(minisnmpstart)
        stackless.schedule(task)
        #execcmd(minisnmpstart)

if __name__ == '__main__':
    n_snmp_daemons = 4
    create_namespaces(n_snmp_daemons)
    setup_veth_per_ns(n_snmp_daemons)
    setup_linux_bridge(n_snmp_daemons)
    add_default_routes_to_ns()
    enable_routing_n_nat()
    start_minisnmpd_per_ns(n_snmp_daemons)
