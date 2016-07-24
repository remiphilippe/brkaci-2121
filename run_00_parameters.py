__author__ = 'mihiguch'

from core import get_one

# Tenant name
entity_name = "SG-Demo1"

# VDC name
ap_name = "ANP"

# L3out encap VLANS
l3out_vlan = 101

### ASA interfaces
_asa_linterfaces = [
    dict(
        name='external',
        type='external'
    ),
    dict(
        name='internal',
        type='internal'
    ),
    dict(
        name='fover_lan',
        type='failover_lan'
    ),
    dict(
        name='fover_link',
        type='failover_link'
    )
]


# Zone's IPs
asa_ext_ip = '172.16.10.1/255.255.255.0'
asa_int_ip = '172.16.11.1/255.255.255.0'
web_bd_svi = '192.168.11.254/24'
app_bd_svi = '192.168.12.254/24'
db_bd_svi = '192.168.13.254/24'

# ASAv VM name, IP and credential
asav_mgmt = dict(
    name='ASAv',
    vmname = entity_name + '-ASAv',
    ip='192.168.1.131',
    username = 'admin',
    password = 'ins3965!'
)

# BIGIP VM name, IP and credential
bigip_mgmt = dict(
    name='BIGIP',
    vmname=entity_name + '-BIGIP',
    ip='192.168.1.141',
    username = 'admin',
    password = 'ins3965!'
)


####################################################
# Nothing needs to be changed from now on
####################################################


entity_dn = 'uni/tn-' + entity_name
ap_dn = entity_dn + '/ap-' + ap_name

lb_node_name = 'ADC'
fw_node_name = 'Firewall'

zone1_dmz_graph_name = "FW-ADC"
zone2_adc_graph_name = "ADC"

asav_name = "ASAv"
bigip_name = "BIGIP"


asav_dn = entity_dn + '/lDevVip-' + asav_name
bigip_dn = entity_dn + '/lDevVip-' + bigip_name


# Now we create an automated VDC
bd_base_dn = entity_dn + '/BD-'
epg_base_dn = ap_dn + '/epg-'
l3out_base_dn = entity_dn + '/out-'

# BDs
asa_ext_bd = bd_base_dn + 'ASA-external'
asa_int_bd = bd_base_dn + 'ASA-internal'
bigip_int_bd = bd_base_dn + 'LB'

# EPG Name
web_name = "Web"
app_name = "App"
db_name = "DB"

# Contracts Name
client_web_name = "Client-" + web_name
web_app_name = web_name + "-" + app_name
app_db_name = app_name  + "-" + db_name


#### BIGIP parameters ####
# BIGIP self IP

bigip_networks = dict(
    network_name = 'Network-All',
    interface_key = 'InternalSelfIP',
    ip='192.168.10.200',
    mask='255.255.255.0'
)
# BIGIP default route
bigip_routes = dict(
    network_name='Network-All',
    destsubnet = '0.0.0.0',
    mask='0.0.0.0',
    nexthop='192.168.10.254'
)

# VIP for Web
web_vip= dict(
    name='Web',
    ip='192.168.10.110',
    port='80'
)

# VIP for App
app_vip = dict(
    name='App',
    ip='192.168.10.120',
    port='5001'
)

# VIP for DB
db_vip = dict(
    name='DB',
    ip='192.168.10.130',
    port='6001'
)