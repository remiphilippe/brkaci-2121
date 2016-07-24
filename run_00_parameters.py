__author__ = 'mihiguch'

# Tenant name
entity_name = "SG-Demo2"

# Application Profile name
ap_name = "ANP"

# L3out encap VLANS
l3out_vlan = 102

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

# ASA IPs
asa_ext_ip = '192.168.100.100/255.255.255.0'
asa_dmz_ip = '192.168.10.254/255.255.255.0'
asa_web_ip = '192.168.11.254/255.255.255.0'
asa_app_ip = '192.168.12.254/255.255.255.0'
asa_db_ip = '192.168.13.254/255.255.255.0'

# ASAv VM name, IP and credential
asav_mgmt = dict(
    name='ASAv',
    vmname = entity_name + '-ASAv',
    ip='192.168.1.132',
    username = 'admin',
    password = 'ins3965!'
)

# Citrix VM name, IP and credential
vpx_mgmt = dict(
    name='VPX',
    vmname=entity_name + '-VPX',
    ip='192.168.1.152',
    username = 'nsroot',
    password = 'nsroot'
)



entity_dn = 'uni/tn-' + entity_name
ap_dn = entity_dn + '/ap-' + ap_name

lb_node_name = 'ADC'
fw_node_name = 'Firewall'

zone1_dmz_graph_name = "FW-ADC"
zone2_fw_graph_name = "FW"

asav_name = "ASAv"
vpx_name = "VPX"

asav_dn = entity_dn + '/lDevVip-' + asav_name
vpx_dn = entity_dn + '/lDevVip-' + vpx_name

# Now we create an automated VDC
bd_base_dn = entity_dn + '/BD-'
epg_base_dn = ap_dn + '/epg-'
l3out_base_dn = entity_dn + '/out-'

# BDs
asa_ext_bd = bd_base_dn + 'ASA-external'
dmz_bd = bd_base_dn + 'DMZ'
web_bd = bd_base_dn + 'Web'
app_bd = bd_base_dn + 'App'
db_bd = bd_base_dn + 'DB'

# EPG Name
web_name = "Web"
app_name = "App"
db_name = "DB"

# Contracts Name
client_web_name = "Client-" + web_name
web_app_name = web_name + "-" + app_name
app_db_name = app_name  + "-" + db_name


#### VPX parameters ####
# VPX SNIP
vpx_networks = dict(
    network_name = 'Network',
    interface_key = 'internal_snip',
    ip='192.168.10.200',
    mask='255.255.255.0',
)

# VPX external route
vpx_ext_routes = dict(
    network_name='Network',
    destsubnet = '10.0.0.0',
    mask='255.0.0.0',
    nexthop='192.168.10.254'
)

# VPX internal route
vpx_int_routes = dict(
    network_name='Network',
    destsubnet = '192.168.0.0',
    mask='255.255.0.0',
    nexthop='192.168.10.254'
)


# VPX VIP
web_vip= dict(
    name='Web',
    ip='192.168.10.110',
    mask= '255.255.255.0',
    port='80',
    network_name = 'Network'
)

# Real servers
web_realservers = [
    dict(
        name='web1',
        ip='192.168.11.1',
        port='80'
    )
]